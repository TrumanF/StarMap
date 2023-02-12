from astropy.coordinates import SkyCoord


class Star:
    def __init__(self, ra, dec, mag, name=None, color="white"):
        self.ra = float(ra) * 15  # degrees
        self.dec = float(dec)  # degrees
        self.mag = float(mag)
        self.az = None  # radians
        self.alt = None  # degrees
        self.normalized_alt = None
        self.coord = SkyCoord(self.ra, self.dec, unit="deg")

        self.name = name
        self.label_print = ""
        self.color = color

        self.x = None
        self.y = None

        self.size = 1  # radius to be plotted

    def __repr__(self):
        return f"({self.name if self.name else 'No name'} | [RA/Dec: ({self.ra}, {self.dec})], [Alt/Az: ({self.alt}, {self.az})] " \
               f"| MAG: {self.mag})\n"
