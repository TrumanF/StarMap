import codecs


XML_HEADER = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
SVG_FOOTER = '</svg>'


# Note: When drawing curves, ask for input of list of points on that curve, with high resolution
# TODO: Change parameters of the functions to match each other's order
# TODO: Figure out how to fit bezier curve to set of points

# NOTE: The problem with this class is that I have to flip y-coordinates because of the nature of how images deal with
#  coordinates. I need to sit down and rethink exactly how I want to do this. Currently, path does not flip y coords.

# https://www.w3schools.com/graphics/svg_intro.asp
class SVG:

    def __init__(self, width, height, background_color="#0e218a"):
        self.elements = []
        self.h, self.w = height, width
        self.background_color = background_color
        self.SVG_HEADER = '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" height="{0}" width="{1}">\n'.format(self.h, self.w) + '<defs><radialGradient id="StarGradient1"><stop offset="70%" stop-color="white"/><stop offset="100%" stop-color="white" stop-opacity="0.25" /></radialGradient></defs>\n'
        # NOTE: Can make background color a parameter of the __init__
        self.background = f'<rect width="100%" height="100%" fill="{self.background_color}" />'
        self.elements.append(self.background)

    def __repr__(self):
        return f'SVG | Elements: {len(self.elements)} | Canvas Size: ({self.h}, {self.w})'

    def line(self, x1, y1, x2, y2, color="white", width=1, opacity=1):
        self.elements.append(f'<line x1="{x1}" y1="{self.h-y1}" x2="{x2}" y2="{self.h-y2}" stroke="{color}" stroke-width="{width}"'
                             f' opacity="{opacity}"/>')


    def circle(self, cx, cy, r, color="white", width=1.0, fill="white", opacity=1):
        self.elements.append(f'<circle cx="{cx}" cy="{self.h-cy}" r="{r}" stroke="{color}" stroke-width="{width}"'
                             f' fill="{fill if fill else "none"}" opacity="{opacity}"/>')


    def rect(self, x, y, width, height, color="white", fill="white", stroke_width=1, rx=0):
        self.elements.append(f'<rect x="{x}" y="{self.h-y}"  width="{width}" height="{height}" stroke="{color}"'
                             f' stroke-width="{stroke_width}" fill="{fill}" rx="{rx}" />')


    def text(self, x, y, txt, color="white", dx=5, dy=5, size=15):
        self.elements.append(f'<text x="{x}" y="{self.h-y}" fill="{color}" dx="{dx}" dy="{-dy}" font-size="{size}px">{txt}</text>')


    def path(self, points, width=5.0, color="white"):
        d = f"M{points[0][0]} {points[0][1]} "
        for point in points[1:]:
            d += f'C{point[0]} {point[1]} '

        self.elements.append(f'<path d="{d}" stroke-width="{width}" stroke="{color}"/>')

    # Note: function from https://github.com/codebox/star-charts/blob/master/svg.py

    def curve(self, _points, width=5.0, color="white", stroke_opacity=1):
        points = sum(_points, ())

        # http://schepers.cc/getting-to-the-point
        # http://schepers.cc/svg/path/catmullrom2bezier.js
        d = 'M {} {} '.format(points[0], points[1])
        i = 0
        iLen = len(points)
        while iLen - 2 > i:
            p = []
            if i == 0:
                p.append((points[i], points[i + 1]))
                p.append((points[i], points[i + 1]))
                p.append((points[i + 2], points[i + 3]))
                p.append((points[i + 4], points[i + 5]))
            elif iLen - 4 == i:
                p.append((points[i - 2], points[i - 1]))
                p.append((points[i], points[i + 1]))
                p.append((points[i + 2], points[i + 3]))
                p.append((points[i + 2], points[i + 3]))
            else:
                p.append((points[i - 2], points[i - 1]))
                p.append((points[i], points[i + 1]))
                p.append((points[i + 2], points[i + 3]))
                p.append((points[i + 4], points[i + 5]))

            i += 2

            bp = []
            bp.append((p[1][0], p[1][1]))
            bp.append((((-(p[0][0]) + 6 * p[1][0] + p[2][0]) / 6), (-(p[0][1]) + 6 * p[1][1] + p[2][1]) / 6))
            bp.append((((p[1][0] + 6 * p[2][0] - p[3][0]) / 6), (p[1][1] + 6 * p[2][1] - p[3][1]) / 6))
            bp.append((p[2][0], p[2][1]))

            d += 'C %s %s, %s %s, %s %s ' % (bp[1][0], bp[1][1], bp[2][0], bp[2][1], bp[3][0], bp[3][1])

        self.elements.append('<path d="{}" stroke="{}" stroke-width="{}" fill-opacity="0" stroke-opacity="{}"/>'.format(d, color, width, stroke_opacity))


    def export(self, file):
        formatted_elements = [f"\t{element}\n" for element in self.elements]
        codecs.open(f'SVG/{file}', 'w', 'utf-8').writelines([XML_HEADER, self.SVG_HEADER] + formatted_elements + [SVG_FOOTER])
        print(f"Successfully generated {file}")


def test():
    test = SVG(1800, 1500)
    test.curve([(100,50), (200, 80), (300, 90), (200, 100), (500, 150), (600, 100), (800, 900)])
    test.export("testPath.svg")


if __name__ == "__main__":
    test()
