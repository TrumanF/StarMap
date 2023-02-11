import codecs


XML_HEADER = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
SVG_FOOTER = '</svg>'


# https://www.w3schools.com/graphics/svg_intro.asp
class SVG:
    def __init__(self, height, width):
        self.elements = []
        self.h, self.w = height, width
        self.SVG_HEADER = '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" height="{0}" width="{1}">\n'.format(self.h, self.w)
        self.background = '<rect width="100%" height="100%" fill="#0e218a" />'
        self.elements.append(self.background)

    def line(self, x1, y1, x2, y2, color="black", width="1", opacity="1"):
        self.elements.append('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" stroke="{4}"  stroke-width="{5}" opacity="{6}"/>'.format(x1, self.h-y1, x2, self.h-y2, color, width, opacity))

    def circle(self, cx, cy, r, color="black", width=1.0, fill=True):
        self.elements.append(f'<circle cx="{cx}" cy="{self.h-cy}" r="{r}" stroke="{color}" stroke-width="{str(width)}" fill="{color if fill else "none"}" />')

    def text(self, x, y, txt, color="black", dx=5, dy=5, size=15):
        self.elements.append(f'<text x="{x}" y="{self.h-y}" fill="{color}" dx="{dx}" dy="{-dy}" font-size="{size}">{txt}</text>')

    def export(self, file):
        formatted_elements = [f"\t{element}\n" for element in self.elements]
        codecs.open(file, 'w', 'utf-8').writelines([XML_HEADER, self.SVG_HEADER] + formatted_elements + [SVG_FOOTER])
        print("Successfully generated SVG")




