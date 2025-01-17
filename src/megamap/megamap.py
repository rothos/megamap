#-----------------------------------------------------------------------------
# PROLOGUE
#-----------------------------------------------------------------------------

# Did you read the README?


#-----------------------------------------------------------------------------
# BEEP BOOP INITIALIZING
#-----------------------------------------------------------------------------

import time, math, re, pdb
import os.path, subprocess
import argparse
from pathlib import Path
import drawsvg as draw
import pygments
import pygments.styles
import pygments.lexers
from importlib.metadata import version
import random

__version__ = version("megamap")

#-----------------------------------------------------------------------------
# TELL ME WHAT YOU WANT BABY
#-----------------------------------------------------------------------------

def get_default_opts():
    return {
        "input_directory": '.',
        "output_filename": 'megamap.png',
        "ignore_hidden": True,      # ignore hidden files & folders
        "style": pygments.styles.get_style_by_name('solarized-dark'),
        "use_zebra_bg": False,      # if true, alternates bg colors among files
        "page_row_padding": 2,      # row units (includes linespacing)
        "page_col_padding": 4,      # column units
        "pagecols":    80,          # column units
        "charheight":   1,          # px
        "charwidth":    1,          # px
        "linespacing":  1,          # px
        "pixelscale":   1,          # dimensionless
        "aspect_ratio": 1.5,        # width/height
        "verbose": False,           # verbose output
        "quiet": False              # suppress all output except final status
    }

# Aspect ratio is width/height. The program will calculate things to make the
# aspect ratio as close as possible to what is specified. Right now it can't
# guarantee exactness.

#-----------------------------------------------------------------------------
# FUNKITRONS
#-----------------------------------------------------------------------------

# Get the (formatted) time since we've started
def now_time(start_time):
    return "%.2fs  " % (time.time() - start_time)

# Get a list of the paths to all files we want to include in this thing.
# We ignore filenames and directories beginning with a dot.
def get_all_file_paths(dirname, ignore_hidden=True, start_time=None, verbose=False):
    # Common non-code files to skip
    skip_files = {
        'LICENSE', 'README', 'CHANGELOG',
        'CONTRIBUTING', 'AUTHORS', 'CODEOWNERS',
        'requirements.txt', 'package.json', 'package-lock.json',
        'Dockerfile'
    }

    # Common non-code file extensions to skip
    skip_extensions = {
        '.txt', '.csv', '.json', '.xml', '.yaml', '.yml', 
        '.md', '.markdown', '.rst', '.log', '.conf', '.ini',
        '.lock', '.toml', '.cfg', '.config', '.pyc'
    }

    if verbose:
        print("Loading files:")

    # Replace the simple pathlist collection with organized collection
    base_files = []
    dir_files = {}  # Dictionary to store directory -> files mapping
    
    for path in Path(dirname).rglob('*'):
        # Ignore hidden files and directories
        if ignore_hidden and (path.name[0] == '.' or str(path)[0] == '.'):
            continue

        # Ignore directories
        if os.path.isdir(path):
            continue

        # Skip common non-code files
        if path.name in skip_files:
            if verbose:
                print(now_time(start_time) + f"Skipping {path.absolute()} - common non-code file")
            continue

        # Skip files with non-code extensions
        if path.suffix.lower() in skip_extensions:
            if verbose:
                print(now_time(start_time) + f"Skipping {path.absolute()} - non-code file extension")
            continue

        # Determine if file is in base directory or subdirectory
        parent = path.parent
        if parent == Path(dirname):
            base_files.append(path)
        else:
            if parent not in dir_files:
                dir_files[parent] = []
            dir_files[parent].append(path)

    # Sort base files alphabetically
    base_files.sort()
    
    # Sort directories alphabetically and sort their files
    sorted_dirs = sorted(dir_files.keys())
    dir_files = {dir_: sorted(dir_files[dir_]) for dir_ in sorted_dirs}
    
    # Combine all files in the desired order
    pathlist = base_files
    for dir_ in sorted_dirs:
        pathlist.extend(dir_files[dir_])

    return pathlist

# Get the contents of a file
def get_contents(path, start_time=None, verbose=False, quiet=False):
    try:
        with open(path.absolute(), 'r') as f:
            contents = f.readlines()

        # Remove trailing whitespace & replace tabs with spaces
        contents = [line.rstrip() for line in contents]
        contents = [line.replace('\t', '    ') for line in contents]

        # Now that we know the file is valid, print the loading message with full path
        if verbose and not quiet:
            print(now_time(start_time) + "Loading " + str(path.absolute()))

        # Return the blob
        return ('\n'.join(contents)).strip()
    except UnicodeDecodeError:
        if verbose and not quiet:
            print(now_time(start_time) + f"Skipping {str(path.absolute())} - not a text file")
        return None
    except Exception as e:
        print(now_time(start_time) + f"Error reading {str(path.absolute())}: {str(e)}")
        return None

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

    width = 2*numpages*opts["page_col_padding"]*opts["charwidth"] \
            + numpages*opts["pagecols"]*opts["charwidth"]

    height = 2*opts["page_row_padding"]*(opts["charheight"] + opts["linespacing"]) \
            + pagerows*opts["charheight"] \
            + opts["linespacing"]*(pagerows - 1)

    return width, height

# Break up a line into words
def break_str_into_lines(string):
    return re.split(r'(\n)', string)

# Lighten a color
# - lighten(color, 1)    => color
# - lighten(color, .95)  => something slightly lighter
# - lighten(color, 1.05) => something slightly darker
def lighten(hexcolor, fraction):
    rgb = hex_to_rgb(hexcolor)
    rgb = tuple(255 - fraction*(255 - float(c)) for c in rgb)
    rgb = tuple(int(max(0,min(c,255))) for c in rgb)
    return rgb_to_hex(rgb)

# Convert a hex color to rgb
def hex_to_rgb(hexcolor):
    hexcolor = hexcolor.strip('#')
    return tuple(int(hexcolor[i:i+2], 16) for i in (0, 2, 4))

# Revert rgb color to hex
def rgb_to_hex(rgb):
    hexes = [hex(c)[2:] for c in rgb]
    for (i, h) in enumerate(hexes):
        if len(h) == 1:
            hexes[i] = h + h
    return '#' + ''.join(hexes)

# The MVP of this program: a rectangle drawing funkitron
def draw_rectangle(drawing, x, y, width, height, color):
    drawing.append(draw.Rectangle(x, y, width, height, fill=color))

def main():
    parser = argparse.ArgumentParser(
        description='Generate a visual map of your codebase'
    )
    parser.add_argument('input_directory', 
                       nargs='?',
                       default='.',
                       help='Directory containing source code to map (default: current directory)')
    parser.add_argument('output_filename',
                       nargs='?',
                       default='megamap.png',
                       help='Output image filename in PNG format (default: megamap.png)')
    parser.add_argument('-v', '--verbose',
                       action='store_true',
                       help='Enable verbose output')
    parser.add_argument('-q', '--quiet',
                       action='store_true',
                       help='Suppress all output except errors')
    parser.add_argument('--version',
                    action='version',
                    version=f'%(prog)s {__version__}',
                    help='Show program version number and exit')
    parser.add_argument('--list-styles',
                    action='store_true',
                    help='List available syntax highlighting styles and exit')
    parser.add_argument('-a', '--aspect-ratio',
                       type=float,
                       default=1.5,
                       help='Target aspect ratio (width/height) for the output image (default: 1.5)')
    parser.add_argument('-b', '--banner',
                       action='store_true',
                       help='Enable banner mode (sets aspect ratio to 5.0)')
    parser.add_argument('--include-hidden',
                       action='store_true',
                       help='Include hidden files and directories in the map')
    parser.add_argument('-s', '--style',
                       default='solarized-dark',
                       help='Syntax highlighting style (use "random" for random style)')
    parser.add_argument('-z', '--zebra',
                       action='store_true',
                       help='Enable zebra striping of background colors between files')
    parser.add_argument('-c', '--cols',
                       type=int,
                       default=80,
                       help='Number of columns per page (default: 80)')
    parser.add_argument('-x', '--scale',
                       type=int,
                       default=1,
                       help='Pixel scale factor (must be integer, default: 1)')
    
    # Start the timer
    start_time = time.time()
    
    # Parse args and merge with defaults
    args = parser.parse_args()
    
    # Handle --list-styles flag
    if args.list_styles:
        print("Available syntax highlighting styles:")
        for style in sorted(pygments.styles.get_all_styles()):
            print(f"  {style}")
        return 0
        
    opts = get_default_opts()
    
    # Update quiet/verbose first
    opts.update({
        "verbose": args.verbose,
        "quiet": args.quiet
    })
    
    # Handle random style selection
    if args.style.lower() == 'random':
        all_styles = list(pygments.styles.get_all_styles())
        selected_style = random.choice(all_styles)
        style = pygments.styles.get_style_by_name(selected_style)
        if not opts["quiet"]:
            print(now_time(start_time) + f"Using random style: {selected_style}")
    else:
        style = pygments.styles.get_style_by_name(args.style)
    
    # Update remaining options
    opts.update({
        "input_directory": args.input_directory,
        "output_filename": args.output_filename,
        "ignore_hidden": not args.include_hidden,
        "style": style,
        "use_zebra_bg": args.zebra,
        "pagecols": args.cols,
        "pixelscale": args.scale,
        "aspect_ratio": 5.0 if args.banner else args.aspect_ratio
    })

    # Yeah ok let's make this easier here
    input_directory  = opts["input_directory"]
    output_filename  = opts["output_filename"]
    ignore_hidden    = opts["ignore_hidden"]
    style            = opts["style"]
    use_zebra_bg     = opts["use_zebra_bg"]
    page_row_padding = opts["page_row_padding"]
    page_col_padding = opts["page_col_padding"]
    pagecols         = opts["pagecols"]
    charheight       = opts["charheight"]
    charwidth        = opts["charwidth"]
    linespacing      = opts["linespacing"]
    pixelscale       = opts["pixelscale"]
    aspect_ratio     = opts["aspect_ratio"]

    # Get a list of all the file paths
    # For a given path in pathlist:
    # - path.name is the filename
    # - str(path) is the relative path
    # - path.absolute() is the absolute path
    pathlist = get_all_file_paths(input_directory, ignore_hidden, start_time, opts["verbose"])

    # Load up the contents of each file
    # Yeah, we hold it all in memory
    fileblobs = [get_contents(path, start_time, opts["verbose"], opts["quiet"]) for path in pathlist]
    
    # Filter out None values from non-text files (in a single pass to maintain alignment)
    valid_items = [(path, blob) for path, blob in zip(pathlist, fileblobs) if blob is not None]
    pathlist = [item[0] for item in valid_items]
    fileblobs = [item[1] for item in valid_items]
    
    if opts["verbose"]:
        print("\nAfter filtering non-text files:")
        for path, blob in zip(pathlist, fileblobs):
            print(f"Path: {path.absolute()} - Content length: {len(blob) if blob else 'None'}")

    #-----------------------------------------------------------------------------
    # PREPROCESSING
    #-----------------------------------------------------------------------------

    # Try to get lexers for each file, skip files where no lexer is found
    valid_files = []
    valid_blobs = []
    if opts["verbose"]:
        print("\nValidating lexers for files:")
    for path, blob in zip(pathlist, fileblobs):
        try:
            lexer = pygments.lexers.guess_lexer_for_filename(path.absolute(), blob)
            valid_files.append(path)
            valid_blobs.append(blob)
            if opts["verbose"]:
                print(f"✓ {path.absolute()} - Valid lexer found: {lexer.name}")
        except Exception as e:
            if opts["verbose"]:
                print(f"✗ {path.absolute()} - Lexer error: {str(e)}")
                print(now_time(start_time) + f"Skipping {path.absolute()} - no lexer found")

    # Update our lists to only include files with valid lexers
    pathlist = valid_files
    fileblobs = valid_blobs
    
    if not opts["quiet"]:
        print(now_time(start_time) + f"{len(pathlist)} valid files found")

    # A list of the line counts
    linecounts = [len(blob.split('\n')) for blob in fileblobs]

    # The total number of rows (lines) is the sum of the linecounts
    # plus the padding rows (two per file). This is actually an
    # upper bound, since some of the padding may be ignored if it
    # occurs at the bottom of the image (ie if pagebreak == filebreak).
    total_rows = sum(linecounts) + 2*page_row_padding*(len(pathlist) - 1)

    # Determine the number of pages we'll need in order to fit the aspect ratio
    numpages, pagerows, width, height, actual_ratio = calc_page_and_image_vars(opts, total_rows)

    # The style defines a bg color for us
    bgcolor = style.background_color

    # Compute two shades, so we can alternate when file changes
    bgcolorlist = [lighten(bgcolor, 0.96), lighten(bgcolor, 1.02)]

    # But do we *really* want the zebra?
    if not use_zebra_bg:
        bgcolorlist = [bgcolor]

    # Create the drawing
    drawing = draw.Drawing(width, height, origin=(0,0), displayInline=False)

    # Draw the background
    drawing.append(draw.Rectangle(0, 0, width, height, fill=bgcolor))


    #-----------------------------------------------------------------------------
    # MEGAMAP GO BRRR
    #-----------------------------------------------------------------------------

    if opts["verbose"]:
        print("\nCalculating aspect ratio:")

    # Print the final ratio & the target
    if not opts["quiet"]:
        print(now_time(start_time) + "Aspect ratio %.2f  (target %.2f)" % (actual_ratio, aspect_ratio))

    # First, draw all the background colors
    # Initial coordinates
    row = row0 = 0
    x = 0
    dx = charwidth*(pagecols + 2*page_col_padding)
    y0 = 0
    ya = yb = y0
    dy = page_row_padding*(charheight + linespacing)

    # Pretend to loop through the files, draw some bg rects
    i = 0
    for i in range(len(fileblobs)):
        # If we've just finished a file,
        # draw a freakin 'tangle
        if i > 0:
            # Add the inter-file padding
            yb  += 2*dy
            row += 2*page_row_padding

            # Draw a freakin 'tangle
            draw_rectangle(drawing, x, ya, dx, yb-ya, bgcolorlist[(i-1) % len(bgcolorlist)])

            # Reset the y_a coord
            ya = yb

        # Pretend to loop through lines
        for j in range(linecounts[i]):
            # Next line
            yb  += charheight + linespacing
            row += 1

            # If we've fallen off the bottom of the page,
            # let's go to the top of the next page
            if row >= pagerows:
                yb += 2*dy
                draw_rectangle(drawing, x, ya, dx, yb-ya, bgcolorlist[i % len(bgcolorlist)])
                x += dx
                row = row0
                ya = yb = y0

    # Finish off dat last 'tangle
    draw_rectangle(drawing, x, ya, dx, height-ya, bgcolorlist[i % len(bgcolorlist)])

    #-----------------------------------------------------------------------------
    # Ok now draw the word blockies

    # Initial coordinates
    row = col = row0 = col0 = 0
    x = x0 = page_col_padding*charwidth
    y = y0 = page_row_padding*(charheight + linespacing)

    # Loop through each of the files & draw away
    if opts["verbose"]:
        print("\nDrawing files:")
    for (i, blob) in enumerate(fileblobs):
        if i > 0:
            # Add the inter-file padding
            y   += 2*page_row_padding*(charheight + linespacing)
            row += 2*page_row_padding

            # If we've fallen off the bottom of the page,
            # let's go to the top of the next page
            if row >= pagerows:
                x0 += charwidth*(pagecols + 2*page_col_padding)
                row = row0
                y = y0

            # Reset the x coord
            x = x0
            col = col0

        # Info about the current file
        filepath = pathlist[i]
        linecount = linecounts[i]

        # Get the right lexer
        try:
            lexer = pygments.lexers.guess_lexer_for_filename(filepath.absolute(), blob)
        except Exception as e:
            if opts["verbose"]:
                print(f"Error getting lexer for {filepath.absolute()}: {str(e)}")
            continue

        # Buckle up, folks
        if opts["verbose"]:
            print(now_time(start_time) + "Drawing %s (%s) %i lines" % (str(filepath.absolute()), lexer.name, linecount))

        # Wanna buy some tokens?
        tokensource = lexer.get_tokens(blob)

        # So many tokens
        for (ttype, fulltoken) in tokensource:

            # Split the token into lines (kind of).
            # (We use regex to split at '\n', but we keep the '\n'
            # in the resulting array, and also sometimes there are
            # empty strings in the array, if the token begins or
            # ends with '\n'. Don't worry, it's chill.)
            lines_kind_of = break_str_into_lines(fulltoken)

            # Loop through the lines in this token
            # for word in lines_kind_of:
            for line in lines_kind_of:

                for word in re.split(r'( )', line):

                    # It happens sometimes
                    if word == '':
                        continue

                    # Break to the next line, resetting/updating the coordinates
                    if word == '\n':
                        # Next line
                        y   += charheight + linespacing
                        row += 1

                        # If we've fallen off the bottom of the page,
                        # let's go to the top of the next page
                        if row >= pagerows:
                            x0 += charwidth*(pagecols + 2*page_col_padding)
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
                    if len(word.strip()) == 0:
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
                        draw_rectangle(drawing, x, y, wordlen*charwidth, charheight, color)

                        # Advance the x coord
                        x += wordlen*charwidth
                        col += wordlen

    #-----------------------------------------------------------------------------
    # GOD SAVE THE SCENE
    #-----------------------------------------------------------------------------

    if opts["verbose"]:
        print("\nSaving output:")

    # Save the drawing
    resx, resy = (width*pixelscale, height*pixelscale)
    if not opts["quiet"]:
        print(now_time(start_time) + "Saving %s (%ix%ipx)" % (output_filename, resx, resy))
    drawing.set_pixel_scale(pixelscale)
    drawing.save_png(output_filename)

    # Let's hope it was fast
    end_time = time.time()
    total_time = end_time - start_time
    if not opts["quiet"]:
        print(now_time(start_time) + 'Done.')
    
    return 0

if __name__ == '__main__':
    exit(main())
