import re


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


class FilterProperties:
    def __init__(self, raw_filters):
        filter_options = ['mag', 'ra', 'dec', 'dist']
        self.raw_filters = raw_filters
        self._filters = []
        for fo in filter_options:
            for f in self.raw_filters:
                raw_string = re.findall(f"{fo}", f)
                if raw_string:
                    test = re.split(raw_string[0], f)
                    results = list(filter(None, test))
                    fs_list = []
                    for param in results:
                        fs = self.FilterSingle()
                        fs.type = fo
                        number = re.findall(r'\d+\.?\d*', param)[0]
                        fs.value = float(number)
                        greater_than = re.search('\d+\.?\d*<=?|>=?\d+\.?\d*', param)
                        equals = re.search('=', param)
                        less_than = re.search('\d+\.?\d*>=?|<=?\d+\.?\d*', param)
                        if less_than:
                            fs.less_than = True
                        if equals:
                            fs.equals = True
                        if greater_than:
                            fs.greater_than = True
                        fs_list.append(fs)
                    self.filters.append(fs_list)

    @property
    def filters(self):
        return self._filters

    class FilterSingle:
        def __init__(self):
            self.less_than = False
            self.equals = False
            self.greater_than = False
            self.value = None
            self.type = None

        def __repr__(self):
            return f'Value: {self.value} | Type: {self.type} | Equals: {self.equals} | ' \
                   f'Greater than: {self.greater_than} | Less than: {self.less_than}'


def main():
    fp = FilterProperties(['9<=mag<=9.05', '6<ra<=12', 'dec=5'])
    print(fp.filters)


if __name__ == "__main__":
    main()