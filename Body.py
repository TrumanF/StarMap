from astropy.coordinates import SkyCoord


class Star:
    def __init__(self, ra, dec, mag, star_hd, bayer, distance=None, name=None, con=None, color="white"):
        self.ra = float(ra) * 15  # comes in as Hour angle so convert to degrees by multiplying 15
        self.dec = float(dec)  # degrees
        self.mag = float(mag)  # unit-less
        self.hd = star_hd
        self.bayer = bayer
        self.dist = distance  # parsec
        self.con = con  # string: shortened name of constellation

        self.az = None  # radians
        self.alt = None  # degrees
        self.normalized_alt = None
        self.coord = SkyCoord(self.ra, self.dec, unit="deg")

        self.name = name
        self.color = color

        # star coordinates after scaling and offsetting on the SVG
        self.x = None
        self.y = None

        self.size = 1  # radius to be plotted

    def __repr__(self):
        return f"({self.name if self.name else 'No name':^10}/{self.bayer if self.bayer else 'No bayer':^6} | " \
               f"RA/Dec: {str((self.ra, self.dec)):^38} | " \
               f"Alt/Az: {str((self.alt, self.az)):^30} | MAG: {self.mag:^10} | Distance (parsec): {self.dist:^20} | " \
               f"X/Y: {str((self.x, self.y)):^20}\n"


class SSO:
    ssos = {'sun': ('yellow', 10), 'moon': ('darkgray', 9), 'mercury': ('gray', 5), 'venus': ('sienna', 5),
            'mars': ('red', 5), 'jupiter': ('sandybrown', 6), 'saturn': ('goldenrod', 6),
            'uranus': ('paleturquoise', 5),
            'neptune': ('royalblue', 5)}

    def __init__(self, name):
        self.name = name
        self.color, self.size = self.ssos[name]
        self.label_print = True
        # all this info is generated in Chart when added, since Chart holds viewing location
        self.coord = None
        self.ra = None
        self.dec = None

        self.az = None
        self.alt = None
        self.normalized_alt = None

        self.x = None
        self.y = None

    def __repr__(self):
        return f'Object: {self.name.capitalize()} | RA/Dec: ({self.ra}, {self.dec})], [Alt/Az: ({self.alt}, {self.az})]'
