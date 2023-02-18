from astropy.coordinates import SkyCoord


class Star:
    def __init__(self, ra, dec, mag, star_id, distance=None, name=None, con=None, color="white"):
        self.ra = float(ra) * 15  # Note: comes in as Hour angle so convert to degrees by multiplying 15
        self.dec = float(dec)  # degrees
        self.mag = float(mag)  # unit-less
        self.id = star_id
        self.dist = distance  # parsec
        self.con = con  # string: shortened name of constellation

        self.az = None  # radians
        self.alt = None  # degrees
        self.normalized_alt = None
        self.coord = SkyCoord(self.ra, self.dec, unit="deg")

        self.name = name
        self.color = color

        self.x = None
        self.y = None

        self.size = 1  # radius to be plotted

    def __repr__(self):
        return f"({self.name if self.name else 'No name':^10} | RA/Dec: {str((self.ra, self.dec)):^38} | " \
               f"Alt/Az: {str((self.alt, self.az)):^30} | MAG: {self.mag:^10} | Distance (parsec): {self.dist:^20} | " \
               f"X/Y: {str((self.x, self.y)):^20}\n"

