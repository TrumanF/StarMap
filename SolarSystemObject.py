from astropy.coordinates import get_body_barycentric, get_body, get_moon
from astropy import units as u
import math


def polar_to_cartesian(r, theta):
    return r*math.cos(theta), r*math.sin(theta)


ssos_list = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']


class SSO:
    def __init__(self, name, aa, color="white"):
        self.name = name
        self.color = color
        self.coord = get_body(name, aa.obstime, aa.location)
        self.ra = self.coord.ra.to_string(unit=u.deg, decimal=True)
        self.dec = self.coord.dec.to_string(unit=u.deg, decimal=True)
        self.altaz_frame = self.coord.transform_to(aa)
        self.az = float(self.altaz_frame.az.to_string(unit=u.rad, decimal=True))
        self.alt = float(self.altaz_frame.alt.to_string(unit=u.deg, decimal=True))
        self.x = None
        self.y = None

    def plot(self, SVG, MAIN_CIRCLE_INFO, mag_info, label_print):
        if self.alt <= 0:
            return
        # mag_info right now is ONLY float of random size to plot object
        MAIN_CIRCLE_R, MAIN_CIRCLE_CX, MAIN_CIRCLE_CY = MAIN_CIRCLE_INFO
        normalize_alt = -1 * (self.alt / 90 - 1)

        # stars with 90 should plot at center, stars with zero should be on edge, so normalize and reverse direction
        x, y = polar_to_cartesian((normalize_alt * MAIN_CIRCLE_R), -self.az + math.pi / 2)
        # -az because AZ increases to the east and add pi/2 to ensure north is up
        self.x, self.y = -x + MAIN_CIRCLE_CX, y + MAIN_CIRCLE_CY
        SVG.circle(self.x, self.y, mag_info, self.color)

        if label_print:
            SVG.text(self.x, self.y, self.name.capitalize(), color="white", dx=5+mag_info)
