#!/usr/bin/env python3

import logging
import math
import sys

try:
    import importlib.machinery
    danmaku2ass = importlib.machinery.SourceFileLoader('danmaku2ass', '../danmaku2ass.py').load_module('danmaku2ass')
except (AttributeError, ImportError):
    import imp
    danmaku2ass = imp.load_source('danmaku2ass', '../danmaku2ass..py')

extcode = 0


def main():
    logging.basicConfig(level=logging.INFO)
    for Y in (120, 360):
        for X in (160, 480):
            for rotY in range(0, 361):
                for rotZ in range(0, 361):
                    trX, trY, outX, outY, outZ, scaleX, scaleY = danmaku2ass.ConvertFlashRotation(rotY, rotZ, X=X, Y=Y, width=640, height=480)
                    logging.info('(%3d, %3d), %4d, %4d => %4d, %4d, %4d, %4d%%' % (X, Y, rotY, rotZ, outX, outY, outZ, scaleX))
                    CompareMatrix(rotY, rotZ, outX, outY, outZ)


def CompareMatrix(rotY, rotZ, outX, outY, outZ):
    def ApproxEqual(a, b, e=0.015):
        assert e >= 0
        a_b = a - b
        if -e < a_b < e:
            return 0
        else:
            return a_b

    def FormatError(i, j, l, r):
        global extcode
        if ApproxEqual(l, r) != 0:
            extcode = 1
            logging.error('l[%s][%s]=%9.6f      r[%s][%s]=%9.6f' % (i, j, l, i, j, r))

    def sind(x):
        return math.sin(x * math.pi / 180.0)

    def cosd(x):
        return math.cos(x * math.pi / 180.0)

    l = cosd(rotY) * cosd(rotZ)
    r = -sind(outX) * sind(outY) * sind(outZ) + cosd(outY) * cosd(outZ)
    FormatError(0, 0, l, r)
    l = cosd(rotY) * sind(rotZ)
    r = -cosd(outX) * sind(outZ)
    FormatError(0, 1, l, r)
    l = sind(rotY)
    r = -sind(outX) * cosd(outY) * sind(outZ) - sind(outY) * cosd(outZ)
    FormatError(0, 2, l, r)
    l = -sind(rotZ)
    r = sind(outX) * sind(outY) * cosd(outZ) + cosd(outY) * sind(outZ)
    FormatError(1, 0, l, r)
    l = cosd(rotZ)
    r = cosd(outX) * cosd(outZ)
    FormatError(1, 1, l, r)
    l = 0
    r = sind(outX) * cosd(outY) * cosd(outZ) - sind(outY) * sind(outZ)
    FormatError(1, 2, l, r)
    l = -sind(rotY) * cosd(rotZ)
    r = cosd(outX) * sind(outY)
    FormatError(2, 0, l, r)
    l = -sind(rotY) * sind(rotZ)
    r = -sind(outX)
    FormatError(2, 1, l, r)
    l = cosd(rotY)
    r = cosd(outX) * cosd(outY)
    FormatError(2, 2, l, r)

if __name__ == '__main__':
    main()
    sys.exit(extcode)
