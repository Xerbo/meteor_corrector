#!/usr/bin/python3
import sys
import argparse
from os.path import basename, dirname, splitext
from math import *
import numpy as np
import cv2


EARTH_RADIUS = 6371


def sat2earth_angle(radius, height, angle):
    '''
    Convert from the viewing angle from a point at (height) above a
    circle to internal angle from the center of the circle.
    See http://ceeserver.cee.cornell.edu/wdp2/cee6150/monograph/615_04_geomcorrect_rev01.pdf page 4.
    '''
    return asin((radius+height)/radius * sin(angle)) - angle


def earth2sat_angle(radius, height, angle):
    '''
    Oppsite of `sat2earth_angle`, convert from a internal angle
    of a circle to the viewing angle of a point at (height).
    '''
    return -atan(sin(angle)*radius / (cos(angle)*radius - (radius+height)))


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(prog='meteor_corrector',
                                     description='Correct the warp at the edges of images from Meteor-M2 satellite (and alike)')

    parser.add_argument('filename', metavar='INPUT', type=str,
                        help='path to the input image')
    parser.add_argument('-s', '--swath', dest='swath', type=int, default=2800,
                        help='swath of the satellite (in km)')
    parser.add_argument('-a', '--altitude', dest='altitude', type=int, default=820,
                        help='altitude of the satellite (in km)')
    parser.add_argument('-o', '--output', dest='output', type=str,
                        help='path of the output image')

    args = parser.parse_args()

    if args.filename is None:
        parser.print_help()

    if args.output is None:
        out_fname = '{}{}{}-corrected.png'.format(
            dirname(sys.argv[1]),
            '' if dirname(sys.argv[1]) == '' else '/',
            splitext(basename(sys.argv[1]))[0]
        )
    else:
        out_fname = args.output

    # Load the image
    src_img = cv2.imread(args.filename)

    # Gracefully handle a non-existent file
    if src_img is None:
        raise FileNotFoundError('Could not open image')

    # Get image diemensions
    src_height, src_width = src_img.shape[:2]

    # Calculate viewing angle
    VIEW_ANGLE = args.swath / EARTH_RADIUS

    # Estimate output size
    correction_factor = sat2earth_angle(EARTH_RADIUS, args.altitude, 0.001)/0.001  # Change at nadir of image
    out_width = int((VIEW_ANGLE/correction_factor) * src_width/2)

    sat_edge = earth2sat_angle(EARTH_RADIUS, args.altitude, VIEW_ANGLE/2)
    abs_corr = np.zeros(out_width)
    for x in range(out_width):
        angle = ((x/out_width)-0.5)*VIEW_ANGLE
        angle = earth2sat_angle(EARTH_RADIUS, args.altitude, angle)
        abs_corr[x] = (angle/sat_edge + 1)/2 * (src_width-2) + 1

    # Deform mesh
    xs, ys = np.meshgrid(
        np.full(out_width, abs_corr, dtype=np.float32),
        np.arange(src_height, dtype=np.float32)
    )

    # Remap the image, with cubic introplation
    out_img = cv2.remap(src_img, xs, ys, cv2.INTER_CUBIC)

    # Sharpen
    amount = 0.3
    radius = 3
    out_img = cv2.addWeighted(out_img, amount+1, cv2.GaussianBlur(out_img, (0, 0), radius), -amount, 0)

    # Write image
    cv2.imwrite(out_fname, out_img)
