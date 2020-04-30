#-----------------------------------------------------------------------------
# PROLOGUE
#-----------------------------------------------------------------------------

# This script requires Python 3 (I am running Python 3.7) and several
# packages. See imports below.
#
# $ python3 gen.py


#-----------------------------------------------------------------------------
# IF ONLY IF ONLY
#-----------------------------------------------------------------------------

# - syntax highlighting options
#   (maybe different langs have diff bg colors)
# - word wrapping options
# - multiple file concat options
# - filetype ordering / file sorting options
# - image aspect ratio output options
#   (exact ratio? nearest? closest to square? blah)
# - multicolumn gutter options / vert spacing between files options
# - border/framing options
# - instead of drawing each pixel, should draw each word as a box
# - since big images take a long time to produce, can we have a 'preview'
#   feature that just saves e.g. the size & background colors (aka langs)?

# # Get all styles from pygments
# from pygments.styles import STYLE_MAP
# STYLE_MAP.keys()


#-----------------------------------------------------------------------------
# BEEP BOOP INITIALIZING
#-----------------------------------------------------------------------------

import time
import math
import re
import subprocess
import drawSvg as draw
from pygments.lexers import guess_lexer, guess_lexer_for_filename
from pygments.styles import get_style_by_name

# Start the timer
start_time = time.time()


#-----------------------------------------------------------------------------
# TELL ME WHAT YOU WANT BABY
#-----------------------------------------------------------------------------

input_filename = 'sample.css'
output_filename = 'example.png'
style = get_style_by_name('monokai')
textcolor = '#222222'
bgcolor = '#ffffff'
numpages = 4
pagecols = 80
border = 5
charheight = 1
charwidth = 1
linespacing = 1
pixelscale = 2


#-----------------------------------------------------------------------------
# FUNKITRONS
#-----------------------------------------------------------------------------

# Get the (formatted) time since we've started
def now_time():
    return "%.2fs  " % (time.time() - start_time)

# Count the number of lines in a file
# https://stackoverflow.com/questions/845058/how-to-get-line-count-of-a-large-file-cheaply-in-python
def count_lines(filename):
    out = subprocess.Popen(['wc', '-l', filename],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT
                         ).communicate()[0]
    return int(out.partition(b' ')[0])

# Get the contents of a file
def get_contents(filename):
    print(now_time() + "Loading " + filename + "...")
    with open(filename) as f:
        contents = f.readlines()

    # Remove trailing whitespace & replace tabs with spaces
    contents = [line.rstrip() for line in contents]
    contents = [line.replace('\t', '    ') for line in contents]

    return '\n'.join(contents).strip()

# Token drawing funkitron
def draw_token(drawing, x, y, width, height, color):
    drawing.append(draw.Rectangle(x, y, width, height, fill=color))

# Break up a line into words
def break_line(line, col_limit):
    return re.split(r'(\s+)', line[0:col_limit])


#-----------------------------------------------------------------------------
# PREPROCESSING
#-----------------------------------------------------------------------------

# Count the rows in the code file
total_rows = count_lines(input_filename)

# Get the contents of the code file
input_filecontent = get_contents(input_filename)

# Determine the number of page rows ( == lines of text on the whole image )
pagerows = math.ceil(total_rows / numpages)

# Width & height of the whole drawing
width = (numpages+1)*border + numpages*pagecols*charwidth
height = 2*border + pagerows*charheight + linespacing*(pagerows-1)

# Create the drawing
drawing = draw.Drawing(width, height, origin=(0,0), displayInline=False)

# Draw the background
drawing.append(draw.Rectangle(0, 0, width, height, fill=bgcolor))

# Initial coordinates
row0 = 0
col0 = 0
x0 = border
y0 = height - border
x = x0
y = y0
row = row0
col = col0

# Get the right lexer
lexer = guess_lexer_for_filename(input_filename, input_filecontent)


#-----------------------------------------------------------------------------
# MEGAMAP GO BRRR
#-----------------------------------------------------------------------------

# Buckle up, folks
print(now_time() + "Drawing %s (%s)..." % (input_filename, lexer.name))

# Wanna buy some tokens?
tokensource = lexer.get_tokens(input_filecontent)

# So many tokens
for (ttype, word) in tokensource:

    if '\n' in word:
        # Break to the next line
        y -= charheight + linespacing
        row += 1

        if row >= pagerows:
            # We've fallen off the bottom of the page
            # Update the coords
            x0 += border + pagecols*charwidth
            row = row0
            y = y0

        # Reset the x coord
        x = x0
        col = col0
        continue

    if col >= pagecols:
        # If we're off the right side of the page,
        # keep going till we hit a newline
        continue

    if not len(word.strip()):
        # This is whitespace
        # Advance the x coord
        x += len(word)*charwidth

    else:
        # This is a real live token
        while ttype not in style.styles or not len(style.styles[ttype]):
            ttype = ttype.parent

        color = style.styles[ttype]

        wordlen = len(word)
        if col + wordlen > pagecols:
            wordlen = pagecols - col

        draw_token(drawing, x, y, wordlen*charwidth, -charheight, color)

        # Advance the x coord
        x += len(word)*charwidth
        col += 1



# # First, loop through the lines
# for (i, line) in enumerate(content):

#     if i > 0 and i % pagerows == 0:
#         # New page
#         page += border + pagecols*charwidth
#         y = y0

#     # Like a typewriter "return" key
#     x = x0 + page

#     # Loop through the words in a line
#     words = break_line(line, pagecols)
#     for (j, word) in enumerate(words):

#         # If this word is not whitespace
#         if len(word.strip()):
#             # Draw the token
#             draw_token(drawing, x, y, len(word)*charwidth, -charheight, textcolor)

#         x += len(word)

#     y -= charheight + linespacing


#-----------------------------------------------------------------------------
# GOD SAVE THE SCENE
#-----------------------------------------------------------------------------

# Save the drawing
print(now_time() + "Saving " + output_filename + "...")
drawing.setPixelScale(pixelscale)
drawing.savePng(output_filename)

end_time = time.time()
total_time = end_time - start_time
print(now_time() + 'Done.')
