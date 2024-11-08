import os
import sys
import pathlib

MAYA_TDD_ROOT_DIR = str(pathlib.Path(__file__).parent.parent.absolute())
os.environ['MAYA_TDD_ROOT_DIR'] = MAYA_TDD_ROOT_DIR

if MAYA_TDD_ROOT_DIR not in sys.path:
    sys.path.insert(0, MAYA_TDD_ROOT_DIR)
