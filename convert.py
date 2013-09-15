#!/usr/bin/env python3

import argparse
import logging
import sys
import xml.dom.minidom


def ProcessComments(comments, f, width, height, bottomReserved, fontface, fontsize, reduced):
    rows = [None]*(height-bottomReserved)

def ReadCommentsBilibili(f, fontsize):
    'Output format: [(timeline, timestamp, no, comment, type, color, size, height)]'
    dom = xml.dom.minidom.parse(f)
    comment_element = dom.getElementsByTagName('d')
    i = 0
    for comment in comment_element:
        try:
            p = str(comment.getAttribute('p')).split(',')
            assert len(p) >= 8
            assert p[1] in ('1', '4', '5')
            c = str(comment.childNodes[0].wholeText).replace('/n', '\\n')
            yield (float(p[0]), int(p[4]), i, c, {'1': 0, '4': 2, '5': 1}[p[1]], int(p[3]), int(p[2])/25.0, (c.count('\\n')+1)*int(p[2])/25.0)
            i += 1
        except (AssertionError, AttributeError, IndexError, TypeError, ValueError):
            logging.warning('Invalid comment: %s' % comment.toxml())
            continue


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', metavar='OUTPUT', help='Output file')
    parser.add_argument('-s', '--size', metavar='WIDTHxHEIGHT', required=True, help='Stage size in pixels')
    parser.add_argument('-fn', '--font', metavar='FONT', help='Specify font face', default='黑体')
    parser.add_argument('-fs', '--fontsize', metavar='SIZE', help='Default font size', type=float, default=25.0)
    parser.add_argument('-p', '--protect', metavar='HEIGHT', help='Reserve blank on the bottom of the stage', type=int, default=0)
    parser.add_argument('-r', '--reduce', action='store_true', help='Reduce the amount of danmakus if stage is full')
    parser.add_argument('file', metavar='FILE', nargs='+', help='Comment file to be processed')
    args = parser.parse_args()
    try:
        width, height = str(args.size).split('x', 1)
        width = int(width)
        height = int(height)
    except ValueError:
        raise ValueError('Invalid stage size: %r' % args.size)
    comments = []
    for i in args.file:
        with open(i, 'r', encoding='utf-8') as f:
            for comment in ReadCommentsBilibili(f, args.fontsize):
                comments.append(comment)
    if args.output:
        fo = open(args.output, 'w', encoding='utf-8', newline='\r\n')
    else:
        fo = sys.stdout
    comments.sort()
    ProcessComments(comments, fo, width, height, args.protect, args.font, args.fontsize, args.reduce)
    if args.output:
        fo.close()
