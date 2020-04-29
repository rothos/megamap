# This script requires Python 3 (I have running Python 3.7).
# $ python3 gen.py

import drawSvg as draw

filename = 'gen.py'

# Get the contents of the code file
with open(filename) as f:
    content = f.readlines()

# Remove trailing whitespace & replace tabs with spaces
content = [x.rstrip() for x in content]
content = [x.replace('\t','    ') for x in content]

# Relevant variables
textcolor = '#222222'
bgcolor = '#ffffff'
numrows = len(content)
numcols = 80
charheight = 3
charwidth = 2

# Compute stuff
width = numcols * charwidth
height = numrows * charheight

# Create the drawing
drawing = draw.Drawing(width, height+2*charheight, origin=(0,0), displayInline=False)

# Draw the background
drawing.append(draw.Rectangle(0, 0, width, height+2*charheight, fill=bgcolor))

# Pixel drawing funkitron
def draw_pixel(drawing, x, y, charwidth, charheight, color):
    drawing.append(draw.Rectangle(x, y, charwidth, charheight, fill=color))

# Loop & draw
x = charwidth
y = height
for line in content:

    x = charwidth
    for (i,char) in enumerate(line):

        if i > numcols - 3:
            continue

        if char != ' ':
            draw_pixel(drawing, x, y, charwidth, charheight, textcolor)

        x += charwidth

    y -= charheight

# Save the drawing
drawing.setPixelScale(2)
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
