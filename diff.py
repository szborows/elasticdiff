#!/usr/bin/env python3
#-*- encoding: utf-8 -*-

import argparse
import elasticsearch
from urllib import parse as urlparse


def diff(es_left, left_index, es_right, right_index):
    left_page = es_left.search(index=left_index, scroll='2m', search_type='scan', size=1000, body={})
    left_sid = left_page['_scroll_id']
    left_scroll_size = left_page['hits']['total']

    left = []
    while (left_scroll_size > 0):
        left_page = es_left.scroll(scroll_id=left_sid, scroll='2m')
        left_sid = left_page['_scroll_id']
        left_scroll_size = len(left_page['hits']['hits'])
        left.extend(left_page['hits']['hits'])

    right_page = es_right.search(index=right_index, scroll='2m', search_type='scan', size=1000, body={})
    right_sid = right_page['_scroll_id']
    right_scroll_size = right_page['hits']['total']

    right = []
    while (right_scroll_size > 0):
        right_page = es_right.scroll(scroll_id=right_sid, scroll='2m')
        right_sid = right_page['_scroll_id']
        right_scroll_size = len(right_page['hits']['hits'])
        right.extend(right_page['hits']['hits'])

    pass

def main(left_index_url, right_index_url):
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

    return diff(es_left, left_index, es_right, right_index)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='elasticdiff')
    argparser.add_argument('left_index_url')
    argparser.add_argument('right_index_url')
    args = argparser.parse_args()
    main(args.left_index_url, args.right_index_url)
