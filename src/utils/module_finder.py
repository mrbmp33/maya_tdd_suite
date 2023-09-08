import inspect
import sys
import pathlib
from types import MethodType, ModuleType
from typing import Union


def test_name_from_object(obj: Union[ModuleType, MethodType, type]) -> Union[str, bool]:
    """Out of a given object, it returns the name of the route necessary for an unittest loader to import it."""


    module_path = pathlib.Path(inspect.getfile(obj))

    paths = list(module_path.parents)
    paths.insert(0, module_path)

    # Build the name of the module and try importing it
    for index, path in enumerate(paths):
        if index > 0:
            module_path = ".".join(
                [str(x.stem) for x in paths[0:index + 1]].__reversed__()
            )
        else:
            module_path = path.stem

        if str(path.parent) in sys.path:
            return str(module_path)

    return False