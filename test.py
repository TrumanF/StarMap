from SVG import SVG
import numpy as np
import math
# Note: When creating this shit for real, I could round up the area asked for so that edges and lines are round ra and
#  dec values
# Note: Figure out a way to plot as many lines are needed as to create even squares along grid

# CANVAS_X = 1800
# CANVAS_Y = 1500
# prototypeSquare = SVG(CANVAS_X, CANVAS_Y)
#
# ra_scope = (4.5*15, 6.5*15)
# ra_range = abs(ra_scope[1] - ra_scope[0])
# dec_scope = (-10, 10)
# dec_range = abs(dec_scope[1] - dec_scope[0])
# print(ra_range, dec_range)
# ra_to_dec_ratio = ra_range/dec_range
# print(ra_to_dec_ratio)
# size = CANVAS_Y * .9
# ra_size = size
# dec_size = ra_size / ra_to_dec_ratio
# x_placement = CANVAS_X/2 - ra_size/2
# y_placement = CANVAS_Y/2 + dec_size/2
# plot_origin = (x_placement, y_placement-dec_size)
#
# prototypeSquare.rect(x_placement, y_placement, ra_size, dec_size, fill="None", stroke_width=5)
# ra_lines = np.linspace(ra_scope[0], ra_scope[1], 7)[1:-1]
# print(ra_lines)
# dec_lines = np.linspace(dec_scope[0], dec_scope[1], 5)
# # Note: As it is, our range is exact, the sides of the chart are the range
# #  Should I add padding to the sides?
# def convert_ra_to_x(ra):
#     normalized_ra = (ra - min(ra_scope)) / ra_range
#     return (plot_origin[0] + ra_size) - (ra_size * normalized_ra)
#
#
# for ra_value in ra_lines:
#     x = convert_ra_to_x(ra_value)
#     prototypeSquare.line(x, plot_origin[1], x, plot_origin[1] + dec_size)
#
#
# def convert_dec_to_y(dec):
#     normalized_dec = (dec - min(dec_scope)) / dec_range
#     return plot_origin[1] + dec_size * normalized_dec
#
# for dec_value in dec_lines:
#     y = convert_dec_to_y(dec_value)
#     prototypeSquare.line(plot_origin[0], y, plot_origin[0] + ra_size, y)
# prototypeSquare.export("PrototypeSquareChart.svg")
# for i, dec_samp in enumerate(dec_sample):
#     curve = []
#     if i == 0 or i == len(ra_sample) - 1:
#         width = 3
#         stroke_opacity = .8
#     else:
#         width = 2
#         stroke_opacity = .25
#     for ra in ra_space:
#         point = self.ra_dec_to_xy(ra, dec_samp)
#         point = (point[0] * self.SCALE + self.CANVAS_CENTER[0], -point[1] * self.SCALE + self.CANVAS_CENTER[1])
#         curve.append(point)
#     self.chartSVG.curve(curve, width=width, stroke_opacity=stroke_opacity)
# for i, ra_samp in enumerate(ra_sample):
#     curve = []
#     if i == 0 or i == len(ra_sample) - 1:
#         width = 3
#         stroke_opacity = .8
#     else:
#         width = 2
#         stroke_opacity = .25
#     for dec in dec_space:
#         point = self.ra_dec_to_xy(ra_samp, dec)
#         point = (point[0] * self.SCALE + self.CANVAS_CENTER[0], -point[1] * self.SCALE + self.CANVAS_CENTER[1])
#         curve.append(point)
#     self.chartSVG.curve(curve, width=width, stroke_opacity=stroke_opacity)
# Note: The goal here is to ensure there's some minimum number of lines on the plot, if the scale is too small
#  then break the divisions down into half hours, and if needed go to quarter hours, but no further than that
#  For dec, do it whole degrees, half degrees, quarter degrees
from math import sin, cos, asin, acos


def ecliptic_to_equatorial(lambda_var, beta):
    lambda_var = math.radians(lambda_var)
    beta = math.radians(beta)
    epsilon = math.radians(23.439)
    # https://aas.aanda.org/articles/aas/full/1998/01/ds1449/node3.html
    dec = asin(sin(beta)*cos(epsilon) + cos(beta)*sin(epsilon)*sin(lambda_var))
    ra = acos((cos(lambda_var)*cos(beta))/cos(dec))
    print(math.degrees(ra))
    ra2 = asin((-sin(beta)*sin(epsilon)+cos(beta)*cos(epsilon)*sin(lambda_var))/cos(dec))
    print(math.degrees(ra2))
    return 0, math.degrees(dec)

print(ecliptic_to_equatorial(270, 0))