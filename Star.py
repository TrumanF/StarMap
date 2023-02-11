import math
from astropy.coordinates import SkyCoord
from astropy import units as u


def polar_to_cartesian(r, theta):
    return r*math.cos(theta), r*math.sin(theta)


def hms_to_deg(time):
    hour, minute, second = [int(t) for t in time.split(":")]
    return (hour * 15) + (minute * 15/60) + (second * 15/3600)


class Star:
    def __init__(self, ra, dec, mag, label=None, color="white"):
        self.ra = float(ra) * 15  # degrees
        self.dec = float(dec)  # degrees
        self.mag = float(mag)
        self.az = None  # radians
        self.alt = None  # degrees
        self.coord = SkyCoord(self.ra, self.dec, unit="deg")

        self.label = label
        self.label_print = ""
        self.color = color

        self.x = None
        self.y = None

    def __repr__(self):
        return f"(RA: {self.ra}, DEC: {self.dec}, MAG: {self.mag})\n"

    def plot(self, SVG, MAIN_CIRCLE_INFO, mag_info, aa, label_print):
        altaz_frame = self.coord.transform_to(aa)
        az = float(altaz_frame.az.to_string(unit=u.rad, decimal=True))
        alt = float(altaz_frame.alt.to_string(unit=u.deg, decimal=True))
        if alt <= 0:
            return
        min_mag, max_mag = mag_info
        MAIN_CIRCLE_R, MAIN_CIRCLE_CX, MAIN_CIRCLE_CY = MAIN_CIRCLE_INFO
        normalize_alt = -1 * (alt / 90 - 1)

        # stars with 90 should plot at center, stars with zero should be on edge, so normalize and reverse direction
        x, y = polar_to_cartesian((normalize_alt * MAIN_CIRCLE_R), -az + math.pi/2)
        # -az because AZ increases to the east and add pi/2 to ensure north is up
        self.x, self.y = -x + MAIN_CIRCLE_CX, y + MAIN_CIRCLE_CY
        SVG.circle(self.x, self.y, 9.75 * (1 - (self.mag - min_mag) / (max_mag - min_mag)) + .25,
                   self.color)

        if label_print and self.label:
            # nan is getting printed sometimes, fix that
            SVG.text(self.x, self.y, self.label, color="white", dx=5+9.75 * (1 - (self.mag - min_mag) / (max_mag - min_mag)) + .25)
