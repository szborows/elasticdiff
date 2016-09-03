#!/usr/bin/env python3
#-*- encoding: utf-8 -*-

import argparse

def main(src_index_url, dest_index_url):
    print('ok')

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='elasticdiff')
    argparser.add_argument('src_index_url')
    argparser.add_argument('dest_index_url')
    args = argparser.parse_args()
    main(args.src_index_url, args.dest_index_url)
