import os
import pathlib
import platform
import shutil
import tempfile
import uuid
from typing import Dict, Optional
import src
from src.utils import config_loader

_config = config_loader.load_config()

_DEFAULT_MAYA_LOCATIONS: Dict[str, str] = {
    'Windows': r'C:/Program Files/Autodesk/Maya{}',
    'Darwin': r'/Applications/Autodesk/maya{}/Maya.app/Contents',
    'Linux': r'/usr/autodesk/maya{}',
}


def get_maya_location(maya_version: int) -> str:
    """Get the location where Maya is installed.

    Args:
        maya_version (int): The version number.
        
    Returns:
        str: The path to where Maya is installed.
    """
    
    # If the code is launched from within Maya, use the env variable
    if 'MAYA_LOCATION' in os.environ.keys():
        return os.environ['MAYA_LOCATION']
    
    # If outside of maya, get the operating system to try and guess the default installation location
    try:
        maya_exe = _DEFAULT_MAYA_LOCATIONS[str(platform.system())].format(maya_version)
        return maya_exe
    except KeyError:
        raise KeyError("Current operating system is not recognized to determine Maya's location.")


def mayapy(maya_version: int) -> str:
    """Get the mayapy executable path.

    Args:
        maya_version (str): The maya version number.
    
    Returns:
        str: The mayapy executable path.
    """
    
    python_exe = '{0}/bin/mayapy'.format(get_maya_location(maya_version))
    
    if platform.system() == 'Windows':
        python_exe += '.exe'
    return python_exe


def create_clean_maya_app_dir(directory: Optional[str] = None) -> str:
    """Creates an empty directory inside the temp directory and copies over a set of default Maya preferences and
    environment files.

    Returns:
        str: The path to the clean MAYA_APP_DIR folder.
    """
    app_dir = pathlib.Path(os.environ['MAYA_TDD_ROOT_DIR']).resolve() / 'clean_maya_app_dir'
    temp_dir = pathlib.Path(tempfile.gettempdir())
    
    if not temp_dir.exists():
        temp_dir.mkdir()
    
    destination = pathlib.Path(directory or temp_dir / f'maya_app_dir_{uuid.uuid4()}').resolve()
    
    if destination.exists():
        shutil.rmtree(str(destination), ignore_errors=False)
    
    # Copy all the contents from the app_dir to the destination folder
    shutil.copytree(app_dir, destination, symlinks=False)
    
    return str(destination)


def set_maya_env_variables():
    """Sets the basic environment variables for Maya to function normally.

    In the event tha this code is running detached from Maya, it will use the modules paths in the configuration file
    as a place to look for modules.
    """

    # Create clean prefs and prepare sterile environ for testing
    maya_app_dir = create_clean_maya_app_dir()

    os.environ['MAYA_APP_DIR'] = maya_app_dir
    # Clear out any MAYA_SCRIPT_PATH value so that we know we're in a clean env.
    os.environ['MAYA_SCRIPT_PATH'] = ''

    # Paths to inspect.
    tests_dirs: list = _config['paths']['tests'] or [_config['default_tests']]
    os.environ.setdefault('MAYA_MODULE_PATH', f"{os.pathsep}".join(tests_dirs))

if __name__ == '__main__':
    print(create_clean_maya_app_dir())
