import math
from SVG import SVG
import numpy as np


def degree_to_rad(angle_list):
    return [math.radians(x) for x in angle_list]


CANVAS_X = 1800
CANVAS_Y = 1500
chart_center = (CANVAS_X/2, CANVAS_Y/2)
chartSVG = SVG(CANVAS_X, CANVAS_Y)


ra_scope = degree_to_rad((0, 5*15))
dec_scope = degree_to_rad((-70, -45))
print(ra_scope)
print(dec_scope)
ra_center = (ra_scope[0] + ra_scope[1])/2
dec_center = (dec_scope[0] + dec_scope[1])/2

ra_range = abs(ra_scope[1] - ra_scope[0])
dec_range = abs(dec_scope[1] - dec_scope[0])

print(ra_range, dec_range)
ra_to_dec_ratio = ra_range/dec_range
print(ra_to_dec_ratio)
size = CANVAS_Y * .9
ra_size = size
dec_size = ra_size / ra_to_dec_ratio

x_placement = chart_center[0] - ra_size/2
y_placement = chart_center[1] + dec_size/2
# chartSVG.rect(x_placement, y_placement, ra_size, dec_size, fill="None", stroke_width=5)
# plot_origin = (x_placement, y_placement-dec_size)


def ra_dec_to_xy(ra, dec):
    delta_ra = ra - ra_center
    x1 = math.cos(dec) * math.sin(delta_ra)
    y1 = math.sin(dec) * math.cos(dec_center) - math.cos(dec) * math.cos(delta_ra) * math.sin(dec_center)
    return x1, y1

SCALE = 1000
ra_space = np.linspace(ra_scope[0], ra_scope[1], 100)
dec_space = np.linspace(dec_scope[0], dec_scope[1], 100)
ra_sample = np.linspace(ra_scope[0], ra_scope[1], 8)
dec_sample = np.linspace(dec_scope[0], dec_scope[1], 8)

for dec_samp in dec_scope:
    curve = []
    for ra in ra_space:
        point = ra_dec_to_xy(ra, dec_samp)
        point = (point[0] * SCALE + chart_center[0], -point[1]*SCALE + chart_center[1])
        #chartSVG.circle(point[0]*SCALE + chart_center[0], point[1]*SCALE + chart_center[1], 3)
        curve.append(point)
    chartSVG.curve(curve)
for dec in dec_space:
    for ra_samp in ra_scope:
        point = ra_dec_to_xy(ra_samp, dec)
        chartSVG.circle(point[0] * SCALE + chart_center[0], point[1] * SCALE + chart_center[1], 3, color='yellow', fill='yellow')
cx, cy = ra_dec_to_xy(ra_scope[0], dec_scope[0])
print(cx, cy)

chartSVG.circle(chart_center[0], chart_center[1], 5)
chartSVG.circle(cx*SCALE + chart_center[0], cy*SCALE + chart_center[1], 5, color='black', fill='black')

chartSVG.export("OrthographicTest.svg")
