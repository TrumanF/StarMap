import math


def degree_to_rad(angle_list):
    return [math.radians(x) for x in angle_list]


class Area:
    def __init__(self, ra_scope, dec_scope):
        # Note: rename ra and dec_set
        self.RA_SCOPE = degree_to_rad(ra_scope)  # rads
        self.DEC_SCOPE = degree_to_rad(dec_scope)  # rads
        self.RA_RANGE = abs(ra_scope[0] - ra_scope[1])
        self.DEC_RANGE = abs(dec_scope[0] - dec_scope[1])
        self.center = ((self.RA_SCOPE[0] + self.RA_SCOPE[1])/2, (self.DEC_SCOPE[0] + self.DEC_SCOPE[1])/2)  # rads


ORION_AREA = Area((4.75*15, 6.5*15), (-12.5, 21))
URSA_MINOR_AREA = Area((14*15, 18*15), (60, 90))
BIG_DIPPER_AREA = Area((10.5*15, 14*15), (45, 65))
