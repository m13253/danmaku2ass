#!/usr/bin/env python3

import argparse
import colorsys
import logging
import math
import sys
import xml.dom.minidom


def ProcessComments(comments, f, width, height, bottomReserved, fontface, fontsize, alpha, lifetime, reduced):
    WriteASSHead(f, width, height, fontface, fontsize, alpha)
    rows = [[None]*(height-bottomReserved), [None]*(height-bottomReserved), [None]*(height-bottomReserved)]
    for i in comments:
        row = 0
        rowmax = height-bottomReserved-i[7]
        while row < rowmax:
            freerows = TestFreeRows(rows, i, row, width, height, bottomReserved, lifetime)
            if freerows >= i[7]:
                MarkCommentRow(rows, i, row)
                WriteComment(f, i, row, width, height, bottomReserved, fontsize, lifetime)
                break
            else:
                row += freerows or 1
        else:
            if not reduced:
                row = FindAlternativeRow(rows, i, height, bottomReserved)
                MarkCommentRow(rows, i, row)
                WriteComment(f, i, row, width, height, bottomReserved, fontsize, lifetime)


def TestFreeRows(rows, c, row, width, height, bottomReserved, lifetime):
    res = 0
    rowmax = height-bottomReserved-c[7]
    while row < rowmax and res < c[7]:
        if c[4] in (1, 2):
            if rows[c[4]][row] and rows[c[4]][row][0]+lifetime > c[0]:
                break
        else:
            if rows[c[4]][row] and rows[c[4]][row][0]+lifetime*c[8]/width > c[0]:
                break
        row += 1
        res += 1
    return res


def FindAlternativeRow(rows, c, height, bottomReserved):
    res = 0
    for row in range(height-bottomReserved-math.ceil(c[7])):
        if not rows[c[4]][row]:
            return row
        elif rows[c[4]][row][1] < rows[c[4]][res][1]:
            res = row
    return res


def MarkCommentRow(rows, c, row):
    for i in range(row, row+math.ceil(c[7])):
        rows[c[4]][i] = c


def WriteComment(f, c, row, width, height, bottomReserved, fontsize, lifetime):
    text = c[3].replace('\\', '\\\\').replace('\n', '\\N')
    if c[4] == 1:
        styles = '{\\an8}{\\pos(%(halfwidth)s, %(row)s)}' % {'halfwidth': round(width/2), 'row': row}
    elif c[4] == 2:
        styles = '{\\an2}{\\pos(%(halfwidth)s, %(row)s)}' % {'halfwidth': round(width/2), 'row': ConvertType2(row, height, bottomReserved)}
    else:
        styles = '{\\move(%(width)s, %(row)s, %(neglen)s, %(row)s)}' % {'width': width, 'row': row, 'neglen': -math.ceil(c[8])}
    if not (-1 < c[6]-fontsize < 1):
        styles += '{\\fs%s}' % round(c[6])
    if c[5] != 0xffffff:
        styles += '{\\c&H%02X%02X%02x&}' % (c[5]&0xff, (c[5]>>8)&0xff, (c[5]>>16)&0xff)
        if c[5] == 0x000000:
            styles += '{\\3c&HFFFFFF&}'
    f.write('Dialogue: 3,%(start)s,%(end)s,Default,,0000,0000,0000,,%(styles)s%(text)s\n' % {'start': ConvertTimestamp(c[0]), 'end': ConvertTimestamp(c[0]+lifetime), 'styles': styles, 'text': text})


def ReadCommentsBilibili(f, fontsize):
    'Output format: [(timeline, timestamp, no, comment, type, color, size, height, width)]'
    dom = xml.dom.minidom.parse(f)
    comment_element = dom.getElementsByTagName('d')
    i = 0
    for comment in comment_element:
        try:
            p = str(comment.getAttribute('p')).split(',')
            assert len(p) >= 8
            assert p[1] in ('1', '4', '5')
            c = str(comment.childNodes[0].wholeText).replace('/n', '\\n')
            size = int(p[2])*fontsize/25.0
            yield (float(p[0]), int(p[4]), i, c, {'1': 0, '4': 2, '5': 1}[p[1]], int(p[3]), size, (c.count('\\n')+1)*size, CalculateLength(c)*size)
            i += 1
        except (AssertionError, AttributeError, IndexError, TypeError, ValueError):
            logging.warning('Invalid comment: %s' % comment.toxml())
            continue


def ConvertTimestamp(timestamp):
    hour, minute = divmod(timestamp, 3600)
    minute, second = divmod(minute, 60)
    centsecond = round(second*100.0)
    return '%d:%02d:%02d.%02d' % (int(hour), int(minute), int(second), centsecond)


def WriteASSHead(f, width, height, fontface, fontsize, alpha):
    f.write(
'''[Script Info]
ScriptType: v4.00+
Collisions: Normal
PlayResX: %(width)s
PlayResY: %(height)s

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default, %(fontface)s, %(fontsize)s, &H%(alpha)02XFFFFFF, &H%(alpha)02XFFFFFF, &H%(alpha)02X000000, &H%(alpha)02X000000, 0, 0, 0, 0, 100, 100, 0.00, 0.00, 1, 1, 0, 7, 20, 20, 20, 0

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
''' % {'width': width, 'height': height, 'fontface': fontface, 'fontsize': round(fontsize), 'alpha': 255-round(alpha*255)}
    )


def NeedWhiteBorder(rgb):
    h, l, s = colorsys.rgb_to_hls(((rgb>>16)&0xff)/255, ((rgb>>8)&0xff)/255, (rgb&0xff)/255)
    return (1/12 < h < 7/12 and l < 1/3) or l < 5/12


def CalculateLength(s):
    return max(map(len, s.split('\n')))


def ConvertType2(row, height, bottomReserved):
    return height-bottomReserved-row


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', metavar='OUTPUT', help='Output file')
    parser.add_argument('-s', '--size', metavar='WIDTHxHEIGHT', required=True, help='Stage size in pixels')
    parser.add_argument('-fn', '--font', metavar='FONT', help='Specify font face', default='黑体')
    parser.add_argument('-fs', '--fontsize', metavar='SIZE', help='Default font size', type=float, default=25.0)
    parser.add_argument('-a', '--alpha', metavar='ALPHA', help='Text opaque', type=float, default=1.0)
    parser.add_argument('-l', '--lifetime', metavar='SECONDS', help='Duration of comment display', type=float, default=5.0)
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
    ProcessComments(comments, fo, width, height, args.protect, args.font, args.fontsize, args.alpha, args.lifetime, args.reduce)
    if args.output:
        fo.close()
