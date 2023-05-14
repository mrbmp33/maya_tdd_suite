import pathlib
import platform
import shutil
import tempfile
import uuid
from typing import Dict, Optional

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
    app_dir = pathlib.Path(_config['paths']['maya_tdd']) / 'clean_maya_app_dir'
    temp_dir = pathlib.Path(tempfile.gettempdir())
    
    if not temp_dir.exists():
        temp_dir.mkdir()
    
    destination = pathlib.Path(directory or temp_dir / f'maya_app_dir_{uuid.uuid4()}')
    
    if destination.exists():
        shutil.rmtree(str(destination), ignore_errors=False)
    
    # Copy all the contents from the app_dir to the destination folder
    shutil.copytree(app_dir, destination)
    
    return destination


if __name__ == '__main__':
    print(create_clean_maya_app_dir())
