#!/usr/bin/python3
'''
meteor_corrector, a polar satellite geometry corrector
Copyright (C) 2020-2022 Xerbo

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import sys
import argparse
from os.path import basename, dirname, splitext
from math import *
import numpy as np
import cv2
import re


EARTH_RADIUS = 6371


def sat2earth_angle(radius, height, angle):
    '''
    Convert from the viewing angle from a point at (height) above a
    circle to internal angle from the center of the circle.
    See https://web.archive.org/web/20200110090856/http://ceeserver.cee.cornell.edu/wdp2/cee6150/monograph/615_04_geomcorrect_rev01.pdf page 4.
    '''
    return asin((radius+height)/radius * sin(angle)) - angle


def earth2sat_angle(radius, height, angle):
    '''
    Opposite of `sat2earth_angle`, convert from a internal angle
    of a circle to the viewing angle of a point at (height).
    '''
    return -atan(sin(angle)*radius / (cos(angle)*radius - (radius+height)))


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        prog='meteor_corrector',
        description='Correct the warp at the edges of images from Meteor-M2 satellite (and alike)'
    )

    parser.add_argument('filename', type=str,
                        help='path to the input image')
    parser.add_argument('-s', '--swath', dest='swath', type=int, default=2800,
                        help='swath of the satellite (in km)')
    parser.add_argument('-a', '--altitude', dest='altitude', type=int, default=820,
                        help='altitude of the satellite (in km)')
    parser.add_argument('-o', '--output', dest='output', type=str,
                        help='path of the corrected image')
    parser.add_argument('-r', '--resolution', dest='resolution', type=float,
                        help='vertical resolution of the input image in km/px')
    parser.add_argument('-f', '--flip', dest='flip', action='store_true',
                        help='flip the image, for northbound passes')

    args = parser.parse_args()

    if args.filename is None:
        parser.print_help()

    if args.output is None:
        out_fname = re.sub("\..*$", "-corrected.png", args.filename)
    else:
        out_fname = args.output

    # Load the image
    src_img = cv2.imread(args.filename, cv2.IMREAD_COLOR | cv2.IMREAD_ANYDEPTH)

    # Gracefully handle a non-existent file
    if src_img is None:
        raise FileNotFoundError('Could not open image')

    # Get image diemensions
    src_height, src_width = src_img.shape[:2]

    # Calculate viewing angle
    VIEW_ANGLE = args.swath / EARTH_RADIUS

    # Estimate output size
    if args.resolution is None:
        correction_factor = sat2earth_angle(EARTH_RADIUS, args.altitude, 0.001)/0.001  # Change at nadir of image
        out_width = int((VIEW_ANGLE/correction_factor) * src_width/2)
    else:
        out_width = int(args.swath/args.resolution)

    sat_edge = earth2sat_angle(EARTH_RADIUS, args.altitude, VIEW_ANGLE/2)
    abs_corr = np.zeros(out_width)
    for x in range(out_width):
        angle = ((x/out_width)-0.5)*VIEW_ANGLE
        angle = earth2sat_angle(EARTH_RADIUS, args.altitude, angle)
        abs_corr[x] = (angle/sat_edge + 1)/2 * src_width

    # Create a deform mesh for cv2.remap
    xs, ys = np.meshgrid(
        np.full(out_width, abs_corr, dtype=np.float32),
        np.arange(src_height, dtype=np.float32)
    )

    # Correct the image
    out_img = cv2.remap(src_img, xs, ys, cv2.INTER_CUBIC)

    # Sharpen
    amount = 0.3
    radius = 3
    out_img = cv2.addWeighted(out_img, amount+1, cv2.GaussianBlur(out_img, (0, 0), radius), -amount, 0)

    if args.flip:
        out_img = cv2.rotate(out_img, cv2.ROTATE_180)

    # Write image
    cv2.imwrite(out_fname, out_img)


if __name__ == '__main__':
    main()
