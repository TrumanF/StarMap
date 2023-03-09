import math


def degree_to_rad(angle_list):
    return [math.radians(x) for x in angle_list]


def rad_to_degree(angle_list):
    return [math.degrees(x) for x in angle_list]


class Area:
    def __init__(self, ra_scope, dec_scope):
        self._RA_SCOPE = degree_to_rad(ra_scope)  # rads
        self._DEC_SCOPE = degree_to_rad(dec_scope)  # rads
        self.RA_RANGE = abs(ra_scope[0] - ra_scope[1])
        self.DEC_RANGE = abs(dec_scope[0] - dec_scope[1])
        self.center = ((self.RA_SCOPE[0] + self.RA_SCOPE[1])/2, (self.DEC_SCOPE[0] + self.DEC_SCOPE[1])/2)  # rads

    def __repr__(self):
        return f'Center: {self.center}'

    @classmethod
    def from_RADec(cls, coord, size):
        ra, dec = coord
        ra_size, dec_size = size
        ra_scope = (ra - ra_size/2, ra + ra_size/2)
        dec_scope = (dec - dec_size/2, dec + dec_size/2)
        return cls(ra_scope, dec_scope)

    @property
    def RA_SCOPE(self, unit='rad'):
        if unit == 'rad':
            return self._RA_SCOPE
        elif unit == 'deg':
            return rad_to_degree(self._RA_SCOPE)
        else:
            raise TypeError("Invalid unit type")

    @property
    def DEC_SCOPE(self, unit='rad'):
        if unit == 'rad':
            return self._DEC_SCOPE
        elif unit == 'deg':
            return rad_to_degree(self._DEC_SCOPE)
        else:
            raise TypeError("Invalid unit type")



ORION_AREA = Area((4.75*15, 6.5*15), (-12.5, 21))
URSA_MINOR_AREA = Area((14*15, 18*15), (60, 90))
BIG_DIPPER_AREA = Area((10.5*15, 14*15), (45, 65))
