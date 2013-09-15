#!/usr/bin/env python3

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', metavar='OUTPUT', help='Output file')
    parser.add_argument('-s', '--size', metavar='WIDTHxHEIGHT', required=True, help='Stage size in pixels')
    parser.add_argument('-r', '--reduce', action='store_true', help='Reduce the amount of danmakus if stage is full')
    parser.add_argument('file', metavar='FILE', nargs='+', help='Comment file to be processed')
    args = parser.parse_args()
    print(repr(args))
