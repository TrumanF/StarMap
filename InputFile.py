import csv
import re

file_name = r'expres_targets'
stars = []
with open(fr'ObservingLists/{file_name}.csv') as csv_file:
    csvFile = csv.reader(csv_file)
    for i, line in enumerate(csvFile):
        if i == 0:
            continue
        stripped_line = [x.strip() for x in line]
        try:
            float([x.strip() for x in line][1])
        except ValueError:
            # check if hms
            match = re.match("[0-9][0-9][\sh][0-9][0-9][\sm][0-9][0-9]\.*[0-9]*(\s*|s|$)", stripped_line[1])
            h, m, s = [float(x) for x in match.group().strip('hms').split()]
            ra_val = h + m/60 + s/3600
        try:
            float([x.strip() for x in line][2])
        except ValueError:
            # check if hms
            match = re.match("(^|[+-])[0-9][0-9][\sd][0-9][0-9][\sm][0-9][0-9]\.*[0-9]*(\s*|s|$)", stripped_line[2])
            d, m, s = [float(x) for x in match.group().strip('dms+-').split()]
            dec_val = d + m/60 + s/3600
        stars.append((stripped_line[0], ra_val, dec_val))
