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
import pdb
import drawSvg as draw
from pygments.lexers import guess_lexer, guess_lexer_for_filename
from pygments.styles import get_style_by_name

# Start the timer
start_time = time.time()


#-----------------------------------------------------------------------------
# TELL ME WHAT YOU WANT BABY
#-----------------------------------------------------------------------------

opts = {
    "input_filename":  'sample.css',
    "output_filename": 'example.png',
    "style": get_style_by_name('monokai'),
    "pagecols":    80,
    "border":      5,
    "charheight":  1,
    "charwidth":   1,
    "linespacing": 1,
    "pixelscale":  1
}

# Aspect ratio is width/height. The program will calculate things to make the
# aspect ratio as close as possible to what is specified. Right now it can't
# guarantee exactness.
opts["aspect_ratio"] = 1.5


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
    print(now_time() + "Loading " + filename)
    with open(filename) as f:
        contents = f.readlines()

    # Remove trailing whitespace & replace tabs with spaces
    contents = [line.rstrip() for line in contents]
    contents = [line.replace('\t', '    ') for line in contents]

    return ('\n'.join(contents)).strip()

# Calculate all the delicious dimensional variables.
# The way we do this is:
# - set numpages = 1, calculate aspect ratio based on that
# - while aspect ratio < target, numpages += 1
# - when we exceed target, determine whether the better
#   aspect ratio was before or after we hit the target
def calc_page_and_image_vars(opts, total_rows):

    # Set our target & starting pagenum val
    target = opts["aspect_ratio"]
    numpages = [1]
    k = 0

    # Calculate the ratio for a single page
    w, h = calc_dimensions(opts, total_rows, numpages[k])
    width = [w]
    height = [h]
    ratio = [width[k]/height[k]]

    # Now loop until we exceed our target
    while ratio[k] < target:
        k += 1
        numpages += [k+1]
        w, h = calc_dimensions(opts, total_rows, numpages[k])
        width += [w]
        height += [h]
        ratio += [width[k]/height[k]]

    # Which aspect ratio was better: the one just below the target,
    # or the one just above?
    if min(abs(target - ratio[k]), abs(target - ratio[k-1])) == abs(target - ratio[k]):
        winner = k
    else:
        winner = k - 1

    # Calculate the number of page rows
    pagerows = math.ceil(total_rows / numpages[winner])

    # Return all the goodies
    return numpages[winner], pagerows, width[winner], height[winner], ratio[winner]

# Calculate the dimensions of an image based on the given options
# and a known number of pages
def calc_dimensions(opts, total_rows, numpages):
    pagerows = math.ceil(total_rows / numpages)

    width = (numpages+1)*opts["border"] \
            + numpages*opts["pagecols"]*opts["charwidth"]

    height = 2*opts["border"] \
             + pagerows*opts["charheight"] \
             + opts["linespacing"]*(pagerows-1)

    return width, height

# Break up a line into words
def break_str_into_lines(string):
    return re.split(r'(\n)', string)

# Token drawing funkitron
def draw_token(drawing, x, y, width, height, color):
    drawing.append(draw.Rectangle(x, y, width, height, fill=color))


#-----------------------------------------------------------------------------
# PREPROCESSING
#-----------------------------------------------------------------------------

# Yeah ok let's make this easier here
input_filename  = opts["input_filename"]
output_filename = opts["output_filename"]
style        = opts["style"]
pagecols     = opts["pagecols"]
border       = opts["border"]
charheight   = opts["charheight"]
charwidth    = opts["charwidth"]
linespacing  = opts["linespacing"]
pixelscale   = opts["pixelscale"]
aspect_ratio = opts["aspect_ratio"]

# The style defines a bg color for us
bgcolor = style.background_color

# Count the rows in the code file
total_rows = count_lines(input_filename)

# Get the contents of the code file
input_filecontent = get_contents(input_filename)

# Determine the number of pages we'll need in order to fit the aspect ratio
numpages, pagerows, width, height, ratio = calc_page_and_image_vars(opts, total_rows)

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

# Print the final ratio & the target
print(now_time() + "Aspect ratio %.2f  (target %.2f)" % (ratio, aspect_ratio))


#-----------------------------------------------------------------------------
# MEGAMAP GO BRRR
#-----------------------------------------------------------------------------

# Buckle up, folks
print(now_time() + "Drawing %s (%s) %i lines" % (input_filename, lexer.name, total_rows))

# Wanna buy some tokens?
tokensource = lexer.get_tokens(input_filecontent)

# So many tokens
for (ttype, fulltoken) in tokensource:

    # Split the token into lines (kind of).
    # (We use regex to split at '\n', but we keep the '\n'
    # in the resulting array, and also sometimes there are
    # empty strings in the array, if the token begins or
    # ends with '\n'. Don't worry, it's chill.)
    lines_kind_of = break_str_into_lines(fulltoken)

    # Loop through the lines
    for (k, word) in enumerate(lines_kind_of):

        # It happens sometimes
        if word == '':
            continue

        # Break to the next line, resetting/updating the coordinates
        if word == '\n':

            # Next line
            y -= charheight + linespacing
            row += 1

            # We've fallen off the bottom of the page, so
            # let's go to the top of the next page
            if row >= pagerows:
                x0 += border + pagecols*charwidth
                row = row0
                y = y0

            # Reset the x coord
            x = x0
            col = col0
            continue

        # If we're off the right side of the page,
        # keep going till we hit a newline
        if col + 1 >= pagecols:
            continue

        # This is whitespace
        # Advance the x coord
        if not len(word.strip()):
            x += len(word)*charwidth
            col += len(word)

        # Otherwise, this is a real live token
        else:
            # Get the color of the token. The ._styles attribute is a little
            # hacky maybe, but less hacky than the .styles attribute, I think.
            # The color is the first item in the list.
            color = '#' + style._styles[ttype][0]

            # If the word is longer than the rest of the space we have in this
            # line, then cut it off.
            wordlen = len(word)
            if col + wordlen > pagecols:
                wordlen = pagecols - col

            # Draw the damn thing, finally.
            draw_token(drawing, x, y, wordlen*charwidth, -charheight, color)

            # Advance the x coord
            x += wordlen*charwidth
            col += wordlen


#-----------------------------------------------------------------------------
# GOD SAVE THE SCENE
#-----------------------------------------------------------------------------

# Save the drawing
print(now_time() + "Saving " + output_filename)
drawing.setPixelScale(pixelscale)
drawing.savePng(output_filename)

# Let's hope it was fast
end_time = time.time()
total_time = end_time - start_time
print(now_time() + 'Done.')
