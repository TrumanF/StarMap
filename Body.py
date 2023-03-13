class Star:
    def __init__(self, ra, dec, mag, hd, bayer, dist=None, name=None, con=None, color="white", **kwargs):
        self.ra = float(ra) * 15  # comes in as Hour angle so convert to degrees by multiplying 15
        self.dec = float(dec)  # degrees
        self.mag = float(mag)  # unit-less
        self.hd = str(hd)
        self.bayer = bayer
        self.dist = dist  # parsec
        self.con = con  # string: shortened name of constellation
        self.name = name
        self.color = color

    def __repr__(self):
        return f"{self.name if self.name else 'No name':^10}/{self.bayer if self.bayer else 'No bayer':^6} | " \
               f"RA/Dec: {str((self.ra, self.dec)):^38} | MAG: {self.mag:^10} | " \
               f"Distance (parsec): {self.dist if self.dist else 'N/A':^20}\n"

    @classmethod
    def from_dict(cls, **kwargs):
        new_star = cls(**kwargs)
        for k, v in kwargs.items():
            setattr(new_star, k, v)
        return new_star


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
