#!/usr/bin/env python3
#-*- encoding: utf-8 -*-

# Copyright 2016 Sławomir Zborowski
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from urllib import parse as urlparse
import argparse
import collections
import difflib
import elasticsearch
import json


def get_id_keys(es, index, type_, id_key):
    body = {
        **({"query": {"type": {"value": type_}}} if type_ is not None else {}),
        "fields": [id_key, "_id"],
    }

    page = es.search(index=index, scroll='2m', search_type='scan', size=1000, body=body)
    sid = page['_scroll_id']
    scroll_size = page['hits']['total']

    results = {}
    while (scroll_size > 0):
        page = es.scroll(scroll_id=sid, scroll='2m')
        sid = page['_scroll_id']
        scroll_size = len(page['hits']['hits'])
        results.update({h['fields'][id_key][0]: h['_id'] for h in page['hits']['hits']})

    return results

def print_only(only, side):
    for element in only:
        print('only in {0}: {1}'.format(side, element))

def make_ordered(d):
    def handle(e):
        if isinstance(e, dict):
            return collections.OrderedDict(sorted(e.items(), key=lambda t: handle(t[0])))
        if isinstance(e, (list, tuple)):
            return [handle(x) for x in e]
        return e
    return handle(d)

def diff_common(es_left, left_index, es_right, right_index, common, quiet):
    diff_entries = 0
    for key_, es_ids in common.items():
        left = make_ordered(es_left.get(index=left_index, id=es_ids[0])['_source'])
        right = make_ordered(es_right.get(index=right_index, id=es_ids[1])['_source'])
        if left != right:
            print('entries for key {0} differ'.format(key_))
            diff_entries += 1
            if not quiet:
                leftj = json.dumps(left, indent=2)
                rightj = json.dumps(right, indent=2)
                for line in difflib.unified_diff(leftj.splitlines(), rightj.splitlines()):
                    print(line)
    return diff_entries

def print_summary(only_left, only_right, common, common_differ):
    print('Summary:')
    print('{} entries only in left index'.format(only_left))
    print('{} entries only in right index'.format(only_right))
    print('{} common entries'.format(common))
    print('  {} of them are the same'.format(common - common_differ))
    print('  {} of them differ'.format(common_differ))


def diff(es_left, left_index, es_right, right_index, type_, id_key, quiet):
    left = get_id_keys(es_left, left_index, type_, id_key)
    right = get_id_keys(es_right, right_index, type_, id_key)

    common_keys = set(left.keys()) & set(right.keys())
    only_left_keys = set(left.keys()) - common_keys
    only_right_keys = set(right.keys()) - common_keys

    print_only(only_left_keys, 'left')
    print_only(only_right_keys, 'right')

    common = collections.defaultdict(lambda: [None, None])
    for k, v in left.items():
        common[k][0] = v
    for k, v in right.items():
        common[k][1] = v
    common = {k: v for k, v in common.items() if None not in v}
    entries_differ = diff_common(es_left, left_index, es_right, right_index, common, quiet)

    print_summary(len(only_left_keys), len(only_right_keys), len(common_keys), entries_differ)

def main(left_index_url, right_index_url, type_, id_key, quiet):
    left_index_url = urlparse.urlparse(left_index_url)
    left_es_url = left_index_url.scheme + '://' +  left_index_url.netloc
    es_left = elasticsearch.Elasticsearch(left_es_url)
    if len(left_index_url.path.split('/')) != 2:
        raise RuntimeError('wrong src index path: {}'.format(left_index_url.path))
    right_index_url = urlparse.urlparse(right_index_url)
    right_es_url = right_index_url.scheme + '://' +  right_index_url.netloc
    es_right = elasticsearch.Elasticsearch(right_es_url)
    if len(right_index_url.path.split('/')) != 2:
        raise RuntimeError('wrong dest index path: {}'.format(right_index_url.path))

    left_indices = [x for x in es_left.indices.get_aliases().keys()]
    left_index = left_index_url.path[1:]

    if left_index not in left_indices:
        raise RuntimeError('left index does not exist!')

    right_indices = [x for x in es_right.indices.get_aliases().keys()]
    right_index = right_index_url.path[1:]

    if right_index not in right_indices:
        raise RuntimeError('right index does not exist!')

    return diff(es_left, left_index, es_right, right_index, type_, id_key, quiet)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='elasticdiff')
    argparser.add_argument('left_index_url')
    argparser.add_argument('right_index_url')
    argparser.add_argument('-t', '--type')
    argparser.add_argument('-i', '--id-key')
    argparser.add_argument('-q', '--quiet', action='store_true')
    args = argparser.parse_args()
    main(args.left_index_url, args.right_index_url, args.type, args.id_key, args.quiet)
