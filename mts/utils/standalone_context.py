"""Module that contains a context manager to initialize and uninitialize Maya in standalone mode.
"""

import logging
import os
import sys
from typing import Optional, List
import maya.standalone


def merge_path():
    """Makes sure all paths in PYTHONPATH are also in sys.path.

    When a maya module is loaded, the *scripts* folder is added to PYTHONPATH, but it doesn't seem
    to be added to sys.path. So we are unable to import any of the python files that are in the
    module/scripts folder. A workaround for this is simply adding the paths to sys ourselves.
    """
    real_sys_path = set([os.path.realpath(p) for p in sys.path])
    python_path = set([os.path.realpath(x) for x in os.environ.get('PYTHONPATH', '').split(os.pathsep)])

    for each in python_path:
        if each not in real_sys_path:
            sys.path.insert(0, each)


class MayaStandaloneContext:
    """Context manager for automatically initializing and un-initializing maya. Beware of incompatibilities with scripts
    running in your *userSetup.py*". If they crash, it will prevent Maya from initializing and un-initializing.

    It also sets an environment variable named `MAYA_STANDALONE` to indicate that the active Maya session is running in
    standalone mode.
    """

    def __init__(self, inject_paths: Optional[List[str]] = None, mute_logger: Optional[str] = None):
        """Initializes the context manager.

        Args:
            inject_paths (Optional[List[str]]): A list of paths to inject to the sys.path variable when initializing
                the standalone app.
            mute_logger Optional[str]: The name of the logger to change when initializing maya in case you have some
                logging in your **userSetup** script.
        """

        self._inject_paths = inject_paths

        if mute_logger:
            logging.getLogger(mute_logger).setLevel(logging.ERROR)

    def __enter__(self):
        try:
            maya.standalone.uninitialize()
        except RuntimeError:
            pass

        # Set identifier that is running in standalone mode
        os.environ['MAYA_STANDALONE'] = str(1)

        # Initialize application
        maya.standalone.initialize(name='python')

        # Patch missing mayapy sys.path and add extra paths
        merge_path()
        if self._inject_paths:
            for p in self._inject_paths:
                sys.path.insert(0, p)

        return self

    def __exit__(self, exc_type, exc_value, exc_trace):
        maya.standalone.uninitialize()
