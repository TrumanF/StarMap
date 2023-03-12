class PlotProperties:
    def __init__(self):
        self.x = None
        self.y = None
        self.size = 1


class AzimuthalProperties(PlotProperties):
    def __init__(self):
        super().__init__()
        self.alt = None
        self.az = None
        self.normalized_alt = None
        self.coord = None

