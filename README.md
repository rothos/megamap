<p align="center">
  <img width="1231" height="300" src="https://raw.githubusercontent.com/rothos/megamap/master/banner.png">
</p>


# Megamap

Megamap is a mega awesome version of the minimap feature of text editors like
Sublime. Give megamap a directory full of source code, and it will
produce a PNG image which is a beautiful birdseye view of all the source code.



## Installation

```bash
pip install megamap
```

## Usage

```bash
megamap [input_directory] [output_filename]
```

Optional arguments:
```
-h, --help            Show this help message and exit
-v, --verbose         Enable verbose output
-q, --quiet          Suppress all output except errors
--version            Show program version number and exit
--list-styles        List available syntax highlighting styles and exit
-a, --aspect-ratio   Target aspect ratio (width/height) for output image (default: 1.5)
-b, --banner         Enable banner mode (sets aspect ratio to 5.0)
--include-hidden     Include hidden files and directories in the map
-s, --style          Syntax highlighting style (use "random" for random style)
-z, --zebra          Enable zebra striping of background colors between files
-c, --cols           Number of columns per page (default: 80)
-x, --scale          Pixel scale factor (must be integer, default: 1)
```

The program will automatically:
- Skip common non-code files (LICENSE, README, etc.)
- Skip files with non-code extensions (.txt, .md, .json, etc.)
- Skip binary and non-text files
- Skip files without a valid syntax highlighter


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


## FAQ

### How are the files sorted?

The files are sorted alphabetically by directory and then by file name,
with files in the base directory first.

### How do I find out what all the syntax highlighting styles are called?

You can either:
1. Run `megamap --list-styles` to see all available styles
2. Use `random` as the style to let megamap choose one randomly

### What about word wrapping?

Not currently supported.
