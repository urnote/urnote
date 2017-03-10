import os
import sys

from note.utils.version import get_version

VERSION = (0, 2, 0, 'alpha', 0)

__version__ = get_version(VERSION)

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
