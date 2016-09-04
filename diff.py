#!/usr/bin/env python3
#-*- encoding: utf-8 -*-

import argparse
import elasticsearch
from urllib import parse as urlparse

def main(left_index_url, right_index_url):
    left_index_url = urlparse.urlparse(left_index_url)
    left_es_url = left_index_url.scheme + '://' +  left_index_url.netloc
    es_src = elasticsearch.Elasticsearch(left_es_url)
    if len(left_index_url.path.split('/')) != 2:
        raise RuntimeError('wrong src index path: {}'.format(left_index_url.path))
    right_index_url = urlparse.urlparse(right_index_url)
    right_es_url = right_index_url.scheme + '://' +  right_index_url.netloc
    es_dest = elasticsearch.Elasticsearch(right_es_url)
    if len(right_index_url.path.split('/')) != 2:
        raise RuntimeError('wrong dest index path: {}'.format(right_index_url.path))

    left_indices = [x for x in es_src.indices.get_aliases().keys()]
    left_index = left_index_url.path[1:]

    if left_index not in left_indices:
        raise RuntimeError('left index does not exist!')

    right_indices = [x for x in es_dest.indices.get_aliases().keys()]
    right_index = right_index_url.path[1:]

    if right_index not in right_indices:
        raise RuntimeError('right index does not exist!')


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='elasticdiff')
    argparser.add_argument('left_index_url')
    argparser.add_argument('right_index_url')
    args = argparser.parse_args()
    main(args.left_index_url, args.right_index_url)
