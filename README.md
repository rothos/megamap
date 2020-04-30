<div style="width:100%;height:200px;background:url('https://raw.githubusercontent.com/rothos/megamap/master/statebus.png') center center no-repeat;"></div>

# Megamap

Megamap is a mega awesome version of the minimap feature of text editors like
Sublime and Atom. Give megamap a directory full of source code, and it will
produce a PNG image which is a beautiful birdseye view of all the source code.



## Installation

Download this repository. Make sure you have Python 3. Maybe you need Python
3.6 or something, I don't know.

You'll need to install some packages, the names of which you can figure out
by the error messages when you try to run the script. At least these:
```
$ pip3 install drawSvg
$ pip3 install pygments
```
Maybe Cairo something too. It's 5am and I don't remember anything.



## Getting started

Put your input (could be any text files; source code works well -- although
maybe a book of poetry would be cool too) into a subdirectory of the project,
call it `input/`. Then run
```
$ python3 gen.py
```
If you're lucky it'll work. There might be errors. This has not been
extensively tested. In fact, I just now got it working.

At the beginning of the script there are a bunch of (what I hope are)
self-explanatory options. (A "page" is a column of the output image.)
```
opts = {
    "input_directory": 'input',
    "output_filename": 'output.png',
    "ignore_hidden": True,      # ignore hidden files & folders
    "style": get_style_by_name('monokai'),
    "use_zebra_bg": False,      # if true, alternates bg colors among files
    "page_row_padding": 2,      # row units (includes linespacing)
    "page_col_padding": 4,      # column units
    "pagecols":    80,          # column units
    "charheight":   1,          # px
    "charwidth":    1,          # px
    "linespacing":  1,          # px
    "pixelscale":   1           # dimensionless
}

# Aspect ratio is width/height. The program will calculate things to make the
# aspect ratio as close as possible to what is specified. Right now it can't
# guarantee exactness.
opts["aspect_ratio"] = 1.5
```

## Pretty pictures

These two images were created using the same input (this program's own source code)
with different parameters:

<p align="center">
  <img width="352" height="320" src="https://raw.githubusercontent.com/rothos/megamap/master/gen.py_1.png">
</p>

<p align="center">
  <img width="402" height="288" src="https://raw.githubusercontent.com/rothos/megamap/master/gen.py_2.png">
</p>

Source code of entire projects can be elegantly illustrated:

<p align="center">
  <img width="1232" height="791" src="https://raw.githubusercontent.com/rothos/megamap/master/statebus.png">
</p>


## Questions I might ask myself in the future when I come back and look at this

### How do I find out what all the syntax highlighting styles are called?

```
from pygments.styles import STYLE_MAP
STYLE_MAP.keys()
```
I get this output:
```
dict_keys(['default', 'emacs', 'friendly', 'colorful', 'autumn', 'murphy', 'manni', 'monokai', 'perldoc', 'pastie', 'borland', 'trac', 'native', 'fruity', 'bw', 'vim', 'vs', 'tango', 'rrt', 'xcode', 'igor', 'paraiso-light', 'paraiso-dark', 'lovelace', 'algol', 'algol_nu', 'arduino', 'rainbow_dash', 'abap', 'solarized-dark', 'solarized-light', 'sas', 'stata', 'stata-light', 'stata-dark', 'inkpot'])
```

### Can you sort the input files somehow?

The `pathlib` module seems to order them out randomly, it's weird. But yeah
there is no built-in feature to do this. It wouldn't be hard to modify the
code to do it.

### Is there a way to put a pretty border or frame around the image?

Not right now. Try imagemagick or something. Or submit a pull request.

### What about word wrapping?

Hahahaha.

Hahahahahahaahahahahahahahahahaahahaha.

No.
