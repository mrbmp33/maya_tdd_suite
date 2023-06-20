import argparse
import os
import inspect
import pathlib
import shutil
import subprocess
import sys

root_dir = str(pathlib.Path(__file__).parent.parent.resolve())

if root_dir not in sys.path:
    sys.path.append(root_dir)
    os.environ.setdefault('MAYA_TDD_ROOT_DIR', root_dir)

def main():
    """Entry point to run python tests for a Maya module from the command line.

        This function will parse the command line arguments and will launch the custom unittest runner module using the
        mayapy interpreter given with the chosen Maya version with a vanilla Maya environment.
        """
    from src.run_tests import run_tests
    from src.utils import maya_locations, config_loader

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

    # Paths to inspect.
    tests_dirs: list = config_loader.load_config()['paths']['tests']
    os.environ['MAYA_MODULE_PATH'] = f"{os.pathsep}".join(tests_dirs)

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        out, error = process.communicate()
        print(out)
    except subprocess.CalledProcessError as pe:
        raise pe
    finally:
        # Clean up the tmp directory with vanilla prefs
        shutil.rmtree(maya_app_dir)


if __name__ == '__main__':
    main()
