import math


def polar_to_cartesian(r, theta):
    return r*math.cos(theta), r*math.sin(theta)


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
