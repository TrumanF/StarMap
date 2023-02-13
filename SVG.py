import codecs


XML_HEADER = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
SVG_FOOTER = '</svg>'


# TODO: Change parameters of the functions to match each other's order
# https://www.w3schools.com/graphics/svg_intro.asp
class SVG:
    def __init__(self, height, width, background_color="#0e218a"):
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
        self.elements.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}"  stroke-width="{width}"'
                             f' opacity="{opacity}"/>')

    def circle(self, cx, cy, r, color="white", width=1.0, fill="white", opacity=1):
        self.elements.append(f'<circle cx="{cx}" cy="{self.h-cy}" r="{r}" stroke="{color}" stroke-width="{width}"'
                             f' fill="{fill if fill else "none"}" opacity="{opacity}"/>')

    def rect(self, x, y, width, height, color="white", fill="white", stroke_width=1, rx=0):
        self.elements.append(f'<rect x="{x}" y="{self.h-y}"  width="{width}" height="{height}" stroke="{color}"'
                             f' stroke-width="{stroke_width}" fill="{fill}" rx="{rx}" />')

    def text(self, x, y, txt, color="white", dx=5, dy=5, size=15):
        self.elements.append(f'<text x="{x}" y="{self.h-y}" fill="{color}" dx="{dx}" dy="{-dy}" font-size="{size}px">{txt}</text>')

    def export(self, file):
        formatted_elements = [f"\t{element}\n" for element in self.elements]
        codecs.open(f'SVG/{file}', 'w', 'utf-8').writelines([XML_HEADER, self.SVG_HEADER] + formatted_elements + [SVG_FOOTER])
        print("Successfully generated SVG")




