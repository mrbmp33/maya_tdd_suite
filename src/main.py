#!/usr/bin/env python
"""

"""

import argparse
import os
import inspect
import pathlib
import shutil
import subprocess
import sys

root_dir = str(pathlib.Path(__file__).absolute().parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import src.run_tests as run_tests
from src.utils import maya_locations, config_loader


def main():
    """Entry point to run python tests for a Maya module from the command line.

    This function will parse the command line arguments and will launch the custom unittest runner module using the
    mayapy interpreter given with the chosen Maya version with a vanilla Maya environment.
    """
    
    # Define and get the arguments from the command line
    parser = argparse.ArgumentParser(description='Runs unit tests for a Maya module')
    parser.add_argument('-m', '--maya', help='Maya version', type=int, default=2022)
    
    parsed_args = parser.parse_args()
    
    # Get the test runner module
    run_tests_py = inspect.getfile(run_tests)
    
    # Build the command that will launch the test runner module using mayapy
    cmd = [maya_locations.mayapy(parsed_args.maya), run_tests_py]
    
    if not pathlib.Path(cmd[0]).exists():
        raise RuntimeError(f"Couldn't find a valid Maya executable with the given version: {parsed_args.maya}")
    
    # Create clean prefs and prepare sterile environ for testing
    maya_app_dir = maya_locations.create_clean_maya_app_dir()
    
    os.environ['MAYA_APP_DIR'] = maya_app_dir
    # Clear out any MAYA_SCRIPT_PATH value so that we know we're in a clean env.
    os.environ['MAYA_SCRIPT_PATH'] = ''
    # Run the tests in this module.
    os.environ['MAYA_MODULE_PATH'] = config_loader.load_config()['paths']['maya_tdd']
    
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        pass
    finally:
        # Clean up the tmp directory with vanilla prefs
        shutil.rmtree(maya_app_dir)


if __name__ == '__main__':
    main()
