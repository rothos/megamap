# This script requires Python 3 (I am running Python 3.7).
# $ python3 gen.py

# In order to make this great:
# - syntax highlighting options
#   (maybe different langs have diff bg colors)
# - word wrapping options
# - multiple file concat options
# - image ratio output options
#   (exact ratio? nearest? closest to square? blah)
# - multicolumn gutter options
# - border/framing options

import drawSvg as draw

filename = 'gen.py'

# Get the contents of the code file
with open(filename) as f:
    content = f.readlines()

# Remove trailing whitespace & replace tabs with spaces
content = [x.rstrip() for x in content]
content = [x.replace('\t', '    ') for x in content]

# Relevant variables
numrows = len(content)
numcols = 80
textcolor = '#222222'
bgcolor = '#ffffff'
charheight = 2
charwidth = 2
linespacing = 1
border = 5
pixelscale = 1

# Width & height of the whole drawing
width = numcols * charwidth + (2 * border)
height = numrows * charheight + (2 * border) + (linespacing * (numrows - 1))

# Create the drawing
drawing = draw.Drawing(width, height, origin=(0,0), displayInline=False)

# Draw the background
drawing.append(draw.Rectangle(0, 0, width, height, fill=bgcolor))

# Pixel drawing funkitron
def draw_pixel(drawing, x, y, charwidth, charheight, color):
    drawing.append(draw.Rectangle(x, y, charwidth, charheight, fill=color))

# Loop & draw
x = border
y = height - border
for line in content:

    x = border
    for (i,char) in enumerate(line):

        if i >= numcols - 2:
            continue

        if char != ' ':
            draw_pixel(drawing, x, y, charwidth, -charheight, textcolor)

        x += charwidth

    y -= charheight + linespacing

# Save the drawing
drawing.setPixelScale(pixelscale)
drawing.saveSvg('example.svg')
drawing.savePng('example.png')


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
