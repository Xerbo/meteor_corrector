#!/usr/bin/python3
import re
import sys
from os.path import basename, splitext
from math import *
import numpy as np
import cv2
from scipy.interpolate import interp1d

# Satellite paramaters, in kilometres
EARTH_RADIUS = 6371
SAT_HEIGHT = 820
SWATH = 3050  # TODO: why does 2800km not work properly?


VIEW_ANGLE = (SWATH / EARTH_RADIUS) * 2


def angular_correction(radius, height, angle):
    '''
    Convert from the viewing angle from a point at (height) above a
    circle to internal angle from the center of the circle.
    See http://ceeserver.cee.cornell.edu/wdp2/cee6150/monograph/615_04_geomcorrect_rev01.pdf page 4.
    '''
    return asin((radius+height)/radius * sin(angle)) - angle


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: {} <input file>".format(sys.argv[0]))
        sys.exit(1)

    out_fname = "{}-corrected.png".format(splitext(basename(sys.argv[1]))[0])

    # Load the image
    src_img = cv2.imread(sys.argv[1])

    # Get image diemensions
    src_height, src_width = src_img.shape[:2]

    out_width = 2700  # TODO: dynamic output widths
    abs_corr = np.zeros(out_width)
    edge_angle = angular_correction(EARTH_RADIUS, SAT_HEIGHT, VIEW_ANGLE)
    for x in range(0, src_width):
        angle = (x/src_width * 2 - 1) * VIEW_ANGLE
        earth_angle = angular_correction(EARTH_RADIUS, SAT_HEIGHT, angle)
        out_x = (earth_angle/edge_angle + 1)/2 * out_width
        abs_corr[int(out_x)] = x

    # Interpolate blank values
    x = np.arange(out_width)
    idx = np.nonzero(abs_corr)
    interp = interp1d(x[idx], abs_corr[idx], fill_value="extrapolate")
    abs_corr = interp(x)

    # Deform mesh
    xs, ys = np.meshgrid(
        np.full(out_width, abs_corr, dtype=np.float32),
        np.arange(src_height, dtype=np.float32)
    )

    # Remap the image, with lanczos4 introplation
    out_img = cv2.remap(src_img, xs, ys, cv2.INTER_LANCZOS4)

    # Sharpen
    amount = 0.3
    radius = 5
    out_img = cv2.addWeighted(out_img, amount+1, cv2.GaussianBlur(out_img, (0, 0), radius), -amount, 0)

    # Write image
    cv2.imwrite(out_fname, out_img)
