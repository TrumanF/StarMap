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

# Note: The goal here is to ensure there's some minimum number of lines on the plot, if the scale is too small
#  then break the divisions down into half hours, and if needed go to quarter hours, but no further than that
#  For dec, do it whole degrees, half degrees, quarter degrees

mi_ra_lines = 4

ra_scope = (4.5*15, 6.5*15)
ra_range = abs(ra_scope[1] - ra_scope[0])
dec_scope = (-10, 10)
dec_range = abs(dec_scope[1] - dec_scope[0])

hour_steps = [x for x in range(math.ceil(ra_scope[0]/15), math.ceil(ra_scope[1]/15))]
if len(hour_steps) < 4:
    steps_needed = 4 - len(hour_steps)
    half_hour_steps = np.arange(ra_scope[0]/15, ra_scope[1]/15, .5)
    print(half_hour_steps)