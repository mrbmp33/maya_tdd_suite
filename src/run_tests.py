import os
import sys

from src.utils.standalone_context import MayaStandalone


def run_tests():
    ...


def run_tests_from_command_line():
    """Runs tests in Maya standalone mode.
    
    This is called when running *src/main.py* from the command line.
    """
    
    
    # Make sure all paths in PYTHONPATH are also in sys.path
    # When a maya module is loaded, the *scripts* folder is added to PYTHONPATH, but it doesn't seem
    # to be added to sys.path. So we are unable to import any of the python files that are in the
    # module/scripts folder. A workaround for this is simply adding the paths to sys ourselves.
    with MayaStandalone:
        realsyspath = [os.path.realpath(p) for p in sys.path]
        pythonpath = os.environ.get('PYTHONPATH', '')
        
        for p in pythonpath.split(os.pathsep):
            p = os.path.realpath(p)  # Make sure symbolic links are resolved
            if p not in realsyspath:
                sys.path.insert(0, p)
        
        run_tests()

