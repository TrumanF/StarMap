import math
from SVG import SVG
import numpy as np


def degree_to_rad(angle_list):
    return [math.radians(x) for x in angle_list]


CANVAS_X = 1800
CANVAS_Y = 1500
chart_center = (CANVAS_X/2, CANVAS_Y/2)
chartSVG = SVG(CANVAS_X, CANVAS_Y)


ra_scope = degree_to_rad((0, 24*15))
dec_scope = degree_to_rad((50, 90))

ra_center = (ra_scope[0] + ra_scope[1])/2
dec_center = (dec_scope[0] + dec_scope[1])/2


ra_range = abs(ra_scope[1] - ra_scope[0])
dec_range = abs(dec_scope[1] - dec_scope[0])

ra_to_dec_ratio = ra_range/dec_range

size = CANVAS_Y * .9
ra_size = size
dec_size = ra_size / ra_to_dec_ratio

x_placement = chart_center[0] - ra_size/2
y_placement = chart_center[1] + dec_size/2

Stereo = True

def ra_dec_to_xy(ra, dec):
    delta_ra = ra - ra_center
    x1 = math.cos(dec) * math.sin(delta_ra)
    y1 = math.sin(dec) * math.cos(dec_center) - math.cos(dec) * math.cos(delta_ra) * math.sin(dec_center)
    z1 = math.sin(dec) * math.sin(dec_center) + math.cos(dec) * math.cos(dec_center) * math.cos(delta_ra)
    if Stereo:
        if z1 < -.95:
            d = 20 * math.sqrt((1 - .81) / (1.00000001 - z1 * z1))
        else:
            d = 2 / (z1 + 1)
    else:
        d = 1
    return x1 * d, y1 * d

SCALE = 500
ra_space = np.linspace(ra_scope[0], ra_scope[1], 100)
dec_space = np.linspace(dec_scope[0], dec_scope[1], 100)
ra_sample = np.linspace(ra_scope[0], ra_scope[1], 8)
dec_sample = np.linspace(dec_scope[0], dec_scope[1], 8)

for dec_samp in dec_sample:
    curve = []
    for ra in ra_space:
        point = ra_dec_to_xy(ra, dec_samp)
        point = (point[0] * SCALE + chart_center[0], -point[1]*SCALE + chart_center[1])
        curve.append(point)
    chartSVG.curve(curve)
for ra_samp in ra_sample:
    curve = []
    for dec in dec_space:
        point = ra_dec_to_xy(ra_samp, dec)
        point = (point[0] * SCALE + chart_center[0], -point[1] * SCALE + chart_center[1])
        curve.append(point)
    chartSVG.curve(curve)
cx, cy = ra_dec_to_xy(ra_scope[0], dec_scope[0])
print(cx, cy)

chartSVG.circle(chart_center[0], chart_center[1], 5)
chartSVG.circle(cx*SCALE + chart_center[0], cy*SCALE + chart_center[1], 5, color='black', fill='black')

chartSVG.export("OrthographicTest.svg")
