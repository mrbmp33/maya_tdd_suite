import maya.standalone as standalone
import maya.cmds as mc

import src.utils.maya_locations


class MayaStandalone:
    """Context manager for automatically initializing and un-initializing maya."""
    
    def __enter__(self):
        standalone.initialize()
    
    def __exit__(self, exc_type, exc_value):
        standalone.uninitialize()


if __name__ == '__main__':
    # Example usage:
    with MayaStandalone(2022) as cm:
        mc.polyCube()
