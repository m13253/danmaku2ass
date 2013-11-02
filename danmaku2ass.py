#!/usr/bin/env python3

import argparse
import calendar
import colorsys
import gettext
import json
import logging
import math
import os
import random
import sys
import time
import xml.dom.minidom


__all__ = ["Danmaku2ASS"]


gettext.install('danmaku2ass', os.path.join(os.path.dirname(os.path.abspath(os.path.realpath(sys.argv[0] or 'locale'))), 'locale'))


def SeekZero(function):
    def decorated_function(file_):
        file_.seek(0)
        try:
            return function(file_)
        finally:
            file_.seek(0)
    return decorated_function


def EOFAsNone(function):
    def decorated_function(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except EOFError:
            return None
    return decorated_function


@SeekZero
@EOFAsNone
def ProbeCommentFormat(f):
    tmp = f.read(1)
    if tmp == '[':
        return 'Acfun'
    elif tmp == '{':
        tmp = f.read(14)
        if tmp == '"status_code":':
            return 'Tudou'
        elif tmp == '"root":{"total':
            return 'sH5V'
    elif tmp == '<':
        tmp = f.read(1)
        if tmp == '?':
            tmp = f.read(38)
            if tmp == 'xml version="1.0" encoding="UTF-8"?><p':
                return 'Niconico'
            elif tmp == 'xml version="1.0" encoding="UTF-8"?><i':
                return 'Bilibili'
            elif tmp == 'xml version="1.0" encoding="utf-8"?><i':
                return 'Bilibili'  # tucao.cc, with the same file format as Bilibili
            elif tmp == 'xml version="1.0" encoding="Utf-8"?>\n<':
                return 'Bilibili'  # Komica, with the same file format as Bilibili
            elif tmp == 'xml version="1.0" encoding="UTF-8"?>\n<':
                return 'MioMio'
        elif tmp == 'p':
            return 'Niconico'  # Himawari Douga, with the same file format as Niconico Douga


#
# ReadComments**** protocol
#
# Input:
#     f:         Input file
#     fontsize:  Default font size
#
# Output:
#     yield a tuple:
#         (timeline, timestamp, no, comment, pos, color, size, height, width)
#     timeline:  The position when the comment is replayed
#     timestamp: The UNIX timestamp when the comment is submitted
#     no:        A sequence of 1, 2, 3, ..., used for sorting
#     comment:   The content of the comment
#     pos:       0 for regular moving comment,
#                1 for bottom centered comment,
#                2 for top centered comment
#     color:     Font color represented in 0xRRGGBB,
#                e.g. 0xffffff for white
#     size:      Font size
#     height:    The estimated height in pixels
#                i.e. (comment.count('\n')+1)*size
#     width:     The estimated width in pixels
#                i.e. CalculateLength(comment)*size
#
# After implementing ReadComments****, make sure to update ProbeCommentFormat
# and CommentFormatMap.
#


def ReadCommentsNiconico(f, fontsize):
    NiconicoColorMap = {'red': 0xff0000, 'pink': 0xff8080, 'orange': 0xffc000, 'yellow': 0xffff00, 'green': 0x00ff00, 'cyan': 0x00ffff, 'blue': 0x0000ff, 'purple': 0xc000ff, 'black': 0x000000}
    dom = xml.dom.minidom.parse(f)
    comment_element = dom.getElementsByTagName('chat')
    for comment in comment_element:
        try:
            c = str(comment.childNodes[0].wholeText)
            pos = 0
            color = 0xffffff
            size = fontsize
            for mailstyle in str(comment.getAttribute('mail')).split():
                if mailstyle == 'ue':
                    pos = 1
                elif mailstyle == 'shita':
                    pos = 2
                elif mailstyle == 'big':
                    size = fontsize*1.44
                elif mailstyle == 'small':
                    size = fontsize*0.64
                elif mailstyle in NiconicoColorMap:
                    color = NiconicoColorMap[mailstyle]
            yield (max(int(comment.getAttribute('vpos')), 0)*0.01, int(comment.getAttribute('date')), int(comment.getAttribute('no')), c, pos, color, size, (c.count('\n')+1)*size, CalculateLength(c)*size)
        except (AssertionError, AttributeError, IndexError, TypeError, ValueError):
            logging.warning(_('Invalid comment: %s') % comment.toxml())
            continue


def ReadCommentsAcfun(f, fontsize):
    comment_element = json.load(f)
    i = 0
    for comment in comment_element:
        try:
            p = str(comment['c']).split(',')
            assert len(p) >= 6
            assert p[2] in ('1', '2', '4', '5')
            c = str(comment['m'])
            size = int(p[3])*fontsize/25.0
            yield (float(p[0]), int(p[5]), i, c, {'1': 0, '2': 0, '4': 2, '5': 1}[p[2]], int(p[1]), size, (c.count('\n')+1)*size, CalculateLength(c)*size)
            i += 1
        except (AssertionError, AttributeError, IndexError, TypeError, ValueError):
            logging.warning(_('Invalid comment: %r') % comment)
            continue


def ReadCommentsBilibili(f, fontsize):
    dom = xml.dom.minidom.parse(f)
    comment_element = dom.getElementsByTagName('d')
    i = 0
    for comment in comment_element:
        try:
            p = str(comment.getAttribute('p')).split(',')
            assert len(p) >= 5
            assert p[1] in ('1', '4', '5')
            c = str(comment.childNodes[0].wholeText).replace('/n', '\\n')
            size = int(p[2])*fontsize/25.0
            yield (float(p[0]), int(p[4]), i, c, {'1': 0, '4': 2, '5': 1}[p[1]], int(p[3]), size, (c.count('\n')+1)*size, CalculateLength(c)*size)
            i += 1
        except (AssertionError, AttributeError, IndexError, TypeError, ValueError):
            logging.warning(_('Invalid comment: %s') % comment.toxml())
            continue


def ReadCommentsTudou(f, fontsize):
    comment_element = json.load(f)
    i = 0
    for comment in comment_element['comment_list']:
        try:
            assert comment['pos'] in (3, 4, 6)
            c = str(comment['data'])
            assert comment['size'] in (0, 1, 2)
            size = {0: 0.64, 1: 1, 2: 1.44}[comment['size']]*fontsize
            yield (int(comment['replay_time']*0.001), int(comment['commit_time']), i, c, {3: 0, 4: 2, 6: 1}[comment['pos']], int(comment['color']), size, (c.count('\n')+1)*size, CalculateLength(c)*size)
            i += 1
        except Exception:
            raise
        except (AssertionError, AttributeError, IndexError, TypeError, ValueError):
            logging.warning(_('Invalid comment: %r') % comment)
            continue


def ReadCommentsMioMio(f, fontsize):
    NiconicoColorMap = {'red': 0xff0000, 'pink': 0xff8080, 'orange': 0xffc000, 'yellow': 0xffff00, 'green': 0x00ff00, 'cyan': 0x00ffff, 'blue': 0x0000ff, 'purple': 0xc000ff, 'black': 0x000000}
    dom = xml.dom.minidom.parse(f)
    comment_element = dom.getElementsByTagName('data')
    i = 0
    for comment in comment_element:
        try:
            message = comment.getElementsByTagName('message')[0]
            c = str(message.childNodes[0].wholeText)
            pos = 0
            size = int(message.getAttribute('fontsize'))*fontsize/25.0
            yield (float(comment.getElementsByTagName('playTime')[0].childNodes[0].wholeText), int(calendar.timegm(time.strptime(comment.getElementsByTagName('times')[0].childNodes[0].wholeText, '%Y-%m-%d %H:%M:%S')))+28800, i, c, {'1': 0, '4': 2, '5': 1}[message.getAttribute('mode')], int(message.getAttribute('color')), size, (c.count('\n')+1)*size, CalculateLength(c)*size)
            i += 1
        except (AssertionError, AttributeError, IndexError, TypeError, ValueError):
            logging.warning(_('Invalid comment: %s') % comment.toxml())
            continue


def ReadCommentsSH5V(f, fontsize):
    comment_element = json.load(f)
    i = 0
    for comment in comment_element["root"]["bgs"]:
        try:
            c_at = str(comment['at'])
            c_type = str(comment['type'])
            c_date = str(comment['timestamp'])
            c_color = str(comment['color'])
            c = str(comment['text'])
            size = fontsize
            yield (float(c_at), int(c_date), i, c, {'0': 0, '1': 0, '4': 2, '5': 1}[c_type], int(c_color[1:], 16), size, (c.count('\n')+1)*size, CalculateLength(c)*size)
            i += 1
        except (AssertionError, AttributeError, IndexError, TypeError, ValueError):
            logging.warning(_('Invalid comment: %r') % comment)
            continue


CommentFormatMap = {None: None, 'Niconico': ReadCommentsNiconico, 'Acfun': ReadCommentsAcfun, 'Bilibili': ReadCommentsBilibili, 'Tudou': ReadCommentsTudou, 'MioMio': ReadCommentsMioMio, 'sH5V': ReadCommentsSH5V}


def ProcessComments(comments, f, width, height, bottomReserved, fontface, fontsize, alpha, lifetime, reduced):
    styleid = 'Danmaku2ASS_%04x' % random.randint(0, 0xffff)
    WriteASSHead(f, width, height, fontface, fontsize, alpha, styleid)
    rows = [[None]*(height-bottomReserved), [None]*(height-bottomReserved), [None]*(height-bottomReserved)]
    for i in comments:
        row = 0
        rowmax = height-bottomReserved-i[7]
        while row < rowmax:
            freerows = TestFreeRows(rows, i, row, width, height, bottomReserved, lifetime)
            if freerows >= i[7]:
                MarkCommentRow(rows, i, row)
                WriteComment(f, i, row, width, height, bottomReserved, fontsize, lifetime, styleid)
                break
            else:
                row += freerows or 1
        else:
            if not reduced:
                row = FindAlternativeRow(rows, i, height, bottomReserved)
                MarkCommentRow(rows, i, row)
                WriteComment(f, i, row, width, height, bottomReserved, fontsize, lifetime, styleid)


def TestFreeRows(rows, c, row, width, height, bottomReserved, lifetime):
    res = 0
    rowmax = height-bottomReserved-c[7]
    while row < rowmax and res < c[7]:
        if c[4] in (1, 2):
            if rows[c[4]][row] and rows[c[4]][row][0]+lifetime > c[0]:
                break
        else:
            if rows[c[4]][row] and rows[c[4]][row][0]+lifetime*(rows[c[4]][row][8]+c[8])/width > c[0]:
                break
        row += 1
        res += 1
    return res


def FindAlternativeRow(rows, c, height, bottomReserved):
    res = 0
    for row in range(height-bottomReserved-math.ceil(c[7])):
        if not rows[c[4]][row]:
            return row
        elif rows[c[4]][row][0] < rows[c[4]][res][0]:
            res = row
    return res


def MarkCommentRow(rows, c, row):
    try:
        for i in range(row, row+math.ceil(c[7])):
            rows[c[4]][i] = c
    except IndexError:
        pass


def WriteASSHead(f, width, height, fontface, fontsize, alpha, styleid):
    f.write(
'''\ufeff
[Script Info]
; Script generated by Danmaku2ASS
; https://github.com/m13253/danmaku2ass
ScriptType: v4.00+
Collisions: Normal
PlayResX: %(width)s
PlayResY: %(height)s

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: %(styleid)s, %(fontface)s, %(fontsize)s, &H%(alpha)02XFFFFFF, &H%(alpha)02XFFFFFF, &H%(alpha)02X000000, &H%(alpha)02X000000, 0, 0, 0, 0, 100, 100, 0.00, 0.00, 1, 1, 0, 7, 20, 20, 20, 0

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
''' % {'width': width, 'height': height, 'fontface': fontface, 'fontsize': round(fontsize), 'alpha': 255-round(alpha*255), 'styleid': styleid}
    )


def WriteComment(f, c, row, width, height, bottomReserved, fontsize, lifetime, styleid):
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
        styles += '{\\c&H%02X%02X%02x&}' % (c[5] & 0xff, (c[5] >> 8) & 0xff, (c[5] >> 16) & 0xff)
        if c[5] == 0x000000:
            styles += '{\\3c&HFFFFFF&}'
    f.write('Dialogue: 3,%(start)s,%(end)s,%(styleid)s,,0000,0000,0000,,%(styles)s%(text)s\n' % {'start': ConvertTimestamp(c[0]), 'end': ConvertTimestamp(c[0]+lifetime), 'styles': styles, 'text': text, 'styleid': styleid})


def CalculateLength(s):
    return max(map(len, s.split('\n')))  # May not be accurate


def ConvertTimestamp(timestamp):
    hour, minute = divmod(timestamp, 3600)
    minute, second = divmod(minute, 60)
    centsecond = round((second-int(second))*100.0)
    return '%d:%02d:%02d.%02d' % (int(hour), int(minute), int(second), centsecond)


def ConvertType2(row, height, bottomReserved):
    return height-bottomReserved-row


def NeedWhiteBorder(rgb):
    h, l, s = colorsys.rgb_to_hls(((rgb >> 16) & 0xff)/255.0, ((rgb >> 8) & 0xff)/255.0, (rgb & 0xff)/255.0)
    return (1/12 < h < 7/12 and l < 1/3) or l < 5/12


def ConvertToFile(filename_or_file, *args, **kwargs):
    if isinstance(filename_or_file, str):
        return open(filename_or_file, *args, **kwargs)
    else:
        return filename_or_file


def Danmaku2ASS(input_files, output_file, stage_width, stage_height, reserve_blank=0, font_face=_('(FONT) sans-serif')[7:], font_size=25.0, text_opaque=1.0, comment_duration=5.0, is_reduce_comments=False):
    comments = []
    for i in input_files:
        with ConvertToFile(i, 'r', encoding='utf-8') as f:
            CommentProcesser = CommentFormatMap[ProbeCommentFormat(f)]
            if not CommentProcesser:
                raise ValueError(_('Unknown comment file format: %s') % i)
            for comment in CommentProcesser(f, font_size):
                comments.append(comment)
    try:
        if output_file:
            fo = ConvertToFile(output_file, 'w', encoding='utf-8', newline='\r\n')
        else:
            fo = sys.stdout
        comments.sort()
        ProcessComments(comments, fo, stage_width, stage_height, reserve_blank, font_face, font_size, text_opaque, comment_duration, is_reduce_comments)
    finally:
        if output_file:
            fo.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', metavar=_('OUTPUT'), help=_('Output file'))
    parser.add_argument('-s', '--size', metavar=_('WIDTHxHEIGHT'), required=True, help=_('Stage size in pixels'))
    parser.add_argument('-fn', '--font', metavar=_('FONT'), help=_('Specify font face'), default=_('(FONT) sans-serif')[7:])
    parser.add_argument('-fs', '--fontsize', metavar=_('SIZE'), help=(_('Default font size')), type=float, default=25.0)
    parser.add_argument('-a', '--alpha', metavar=_('ALPHA'), help=_('Text opaque'), type=float, default=1.0)
    parser.add_argument('-l', '--lifetime', metavar=_('SECONDS'), help=_('Duration of comment display'), type=float, default=5.0)
    parser.add_argument('-p', '--protect', metavar=_('HEIGHT'), help=_('Reserve blank on the bottom of the stage'), type=int, default=0)
    parser.add_argument('-r', '--reduce', action='store_true', help=_('Reduce the amount of comments if stage is full'))
    parser.add_argument('file', metavar=_('FILE'), nargs='+', help=_('Comment file to be processed'))
    args = parser.parse_args()
    try:
        width, height = str(args.size).split('x', 1)
        width = int(width)
        height = int(height)
    except ValueError:
        raise ValueError(_('Invalid stage size: %r') % args.size)
    Danmaku2ASS(args.file, args.output, width, height, args.protect, args.font, args.fontsize, args.alpha, args.lifetime, args.reduce)


if __name__ == '__main__':
    main()
