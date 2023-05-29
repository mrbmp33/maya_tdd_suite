import os
import sys
import pathlib

_MAYA_TDD_ROOT_DIR = pathlib.Path(__file__).parent.parent.absolute()
os.environ['MAYA_TDD_ROOT_DIR'] = str(_MAYA_TDD_ROOT_DIR)

if _MAYA_TDD_ROOT_DIR not in sys.path:
    sys.path.insert(0, str(_MAYA_TDD_ROOT_DIR))
