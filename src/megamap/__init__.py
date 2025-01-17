from .megamap import main
from importlib.metadata import version

try:
    __version__ = version("megamap")
except ImportError:
    # Package is not installed
    __version__ = "unknown"
