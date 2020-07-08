#!/usr/bin/python3
import re
import sys
from os.path import basename, splitext
from math import *
import numpy as np
import cv2

# Satellite paramaters
EARTH_RADIUS = 6371
SAT_HEIGHT = 820
SWATH = 2800
VIEW_ANGLE = SWATH / EARTH_RADIUS


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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: {} <input file> *swath *altitude\nArguemts lead by \"*\" are optional.".format(sys.argv[0]))
        sys.exit(1)

    if len(sys.argv) >= 3:
        SWATH = int(sys.argv[2])
        VIEW_ANGLE = SWATH / EARTH_RADIUS

    if len(sys.argv) >= 4:
        SAT_HEIGHT = int(sys.argv[3])

    out_fname = "{}-corrected.png".format(splitext(basename(sys.argv[1]))[0])

    # Load the image
    src_img = cv2.imread(sys.argv[1])

    # Gracefully handle a non-existent file
    if src_img is None:
        raise FileNotFoundError("Could not open image")

    # Get image diemensions
    src_height, src_width = src_img.shape[:2]

    # Calculate output size
    correction_factor = sat2earth_angle(EARTH_RADIUS, SAT_HEIGHT, 0.001)/0.001  # Change at nadir of image
    out_width = int((VIEW_ANGLE/correction_factor) * src_width/2)

    sat_edge = earth2sat_angle(EARTH_RADIUS, SAT_HEIGHT, VIEW_ANGLE/2)

    abs_corr = np.zeros(out_width)
    for x in range(out_width):
        angle = ((x/out_width)-0.5)*VIEW_ANGLE
        angle = earth2sat_angle(EARTH_RADIUS, SAT_HEIGHT, angle)
        abs_corr[x] = (angle/sat_edge + 1)/2 * (src_width-2) + 1

    # Deform mesh
    xs, ys = np.meshgrid(
        np.full(out_width, abs_corr, dtype=np.float32),
        np.arange(src_height, dtype=np.float32)
    )

    # Remap the image, with lanczos4 introplation
    out_img = cv2.remap(src_img, xs, ys, cv2.INTER_CUBIC)

    # Sharpen
    amount = 0.3
    radius = 3
    out_img = cv2.addWeighted(out_img, amount+1, cv2.GaussianBlur(out_img, (0, 0), radius), -amount, 0)

    # Write image
    cv2.imwrite(out_fname, out_img)
