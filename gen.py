# This script requires Python 3 (I am running Python 3.7).
# $ python3 gen.py

# In order to make this great:
# - syntax highlighting options
#   (maybe different langs have diff bg colors)
# - word wrapping options
# - multiple file concat options
# - filetype ordering / file sorting options
# - image ratio output options
#   (exact ratio? nearest? closest to square? blah)
# - multicolumn gutter options / vert spacing between files options
# - border/framing options
# - instead of drawing each pixel, should draw each word as a box

import drawSvg as draw
import math

filename = 'codesample.txt'

# Get the contents of the code file
with open(filename) as f:
    content = f.readlines()

# Remove trailing whitespace & replace tabs with spaces
content = [x.rstrip() for x in content]
content = [x.replace('\t', '    ') for x in content]

# Relevant variables
numpages = 5
pagerows = math.ceil(len(content) / numpages)
pagecols = 80
textcolor = '#222222'
bgcolor = '#ffffff'
charheight = 1
charwidth = 1
linespacing = 1
border = 5
pixelscale = 1

# Width & height of the whole drawing
width = (numpages+1)*border + numpages*pagecols*charwidth
height = 2*border + pagerows*charheight + linespacing*(pagerows-1)

# Create the drawing
drawing = draw.Drawing(width, height, origin=(0,0), displayInline=False)

# Draw the background
drawing.append(draw.Rectangle(0, 0, width, height, fill=bgcolor))

# Pixel drawing funkitron
def draw_pixel(drawing, x, y, charwidth, charheight, color):
    drawing.append(draw.Rectangle(x, y, charwidth, charheight, fill=color))

# Initial coordinates
page0 = 0
x0 = border
y0 = height - border
x = x0
y = y0
page = page0

# Loop & draw
for (i,line) in enumerate(content):

    if i > 0 and i % pagerows == 0:
        # New page
        page += border + pagecols*charwidth
        y = y0

    x = x0 + page

    for (j,char) in enumerate(line):

        if j >= pagecols:
            continue

        if char != ' ':
            draw_pixel(drawing, x, y, charwidth, -charheight, textcolor)

        x += charwidth

    y -= charheight + linespacing

# Save the drawing
drawing.setPixelScale(pixelscale)
drawing.savePng('example.png')
# drawing.saveSvg('example.svg')


# from pygments import highlight
# from pygments.lexers import PythonLexer
# from pygments.formatters import RawTokenFormatter

# code = "from pygments import abcdefg\n# next thing\nprint 'hello'\nx = 2**4"
# print(highlight(code, PythonLexer(), RawTokenFormatter()))

# # Get all styles
# from pygments.styles import STYLE_MAP
# STYLE_MAP.keys()

# # Load a given style
# from pygments.styles import get_style_by_name
# m = get_style_by_name('monokai')
