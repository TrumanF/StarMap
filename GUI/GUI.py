import tkinter as tk
import cairosvg

cairosvg.svg2png(url=r'../SVG/SquareChart1.svg', write_to=r'../PNG/SquareChart1.png')
from PIL import Image, ImageTk
window = tk.Tk()
window.title('Finder Charts V1.0')
img = Image.open(r'../PNG/SquareChart1.png')
pimg = ImageTk.PhotoImage(img)
size = img.size

frame = tk.Canvas(window, width=size[0], height=size[1])
frame.configure(background='black')
frame.pack()
frame.create_image(0,0,anchor='nw',image=pimg)
window.mainloop()