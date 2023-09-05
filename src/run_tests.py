import importlib
import os
import pathlib
import sys
import typing
import unittest
from typing import Iterable, Optional
from unittest import TextTestRunner, TestSuite, TestLoader, TestCase
from maya_test_result import MayaTestResult

from utils import config_loader

_config = config_loader.load_config()
_blacklist_dirs = _config['blacklist_dir_names']


def add_to_path(path):
    """Add the specified path to the system path.

    @param path: Path to add.
    @return True if path was added. Return false if path does not exist or path was already in sys.path
    """
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)
        return True
    return False


def _module_obj_from_path(file_path: str):
    """Returns a module object from a file path that corresponds to a python module."""

    file_path = pathlib.Path(file_path)
    paths = list(file_path.parents)
    paths.insert(0, file_path)

    # Build the name of the module and try importing it
    for index, path in enumerate(paths):
        if index > 0:
            module_name = ".".join(
                [str(x.stem) for x in paths[0:index+1]].__reversed__()
            )
        else:
            module_name = path.stem
        try:
            return importlib.import_module(module_name, file_path)
        except ModuleNotFoundError:
            continue

    raise ModuleNotFoundError(f"Could not find an importable module for given file: {file_path}")


# ==== TESTS COLLECTION ================================================================================================


def maya_module_tests():
    """Generator function to iterate over all the Maya module tests directories."""
    for path in os.environ['MAYA_MODULE_PATH'].split(os.pathsep):
        p = '{0}/tests'.format(path)
        if os.path.exists(p):
            yield p


def get_tests(paths: Iterable[str] = None,
              specific_test: Optional[str] = None,
              test_suite: Optional[TestSuite] = None) -> TestSuite:
    """Get a *unittest.TestSuite* containing all the desired tests.

    Args:
        paths (Iterable[str]): Optional list of directories and/or modules to search for tests. If omitted, use all
            "tests" directories of the packages found in the MAYA_MODULE_PATH.

        specific_test (Optional[str]): Optional test path to find a specific test such as 'test_mytest.py'.

        test_suite (Optional[TestSuite]): Optional unittest.TestSuite to add the discovered tests to. If omitted a new
            TestSuite will be created.
    Returns:
         TestSuite: The populated TestSuite.
    """

    # Create an empty suite and populate it with all the found tests
    if not test_suite:
        test_suite = TestSuite()

    # For individual tests first
    if specific_test:
        directories_added_to_path = [p for p in paths if add_to_path(p)]
        discovered_suite = TestLoader().loadTestsFromName(specific_test)

        if discovered_suite.countTestCases():
            test_suite.addTests(discovered_suite)

        # Remove the added paths.
        for path in directories_added_to_path:
            sys.path.remove(path)

        return test_suite

    # For finding tests depending on file or directory
    modules, directories = (), ()

    # Treat modules and directories independently
    if paths and isinstance(paths, typing.Collection):
        modules = [mod for mod in paths if os.path.isfile(mod)]
        directories = [directory for directory in paths if os.path.isdir(directory)]

    # Fallback to using default maya directories if none is provided
    if not any((directories, paths)):
        directories = maya_module_tests()

    if directories:
        for each in directories:
            found_tests = unittest.defaultTestLoader.discover(each, pattern="*.py")
            if found_tests.countTestCases():
                test_suite.addTests(found_tests)
    if modules:
        for mod in modules:
            found_tests = unittest.defaultTestLoader.loadTestsFromModule(
                _module_obj_from_path(mod)
            )
            if found_tests:
                test_suite.addTests(found_tests)

    return test_suite


# ==== TEST EXECUTION ==================================================================================================


def run_tests(directories: Iterable[str] = None,
              specific_test: Optional[str] = None,
              test_suite: Optional[TestSuite] = None):
    """Run all the tests in the given paths.

    Args:
        directories (Iterable[str]): A generator or list of paths containing tests to run.
        specific_test (TestCase): Optional name of a specific test to run.
        test_suite (TestSuite): Optional TestSuite to run.  If omitted, a TestSuite will be generated.
    """

    if test_suite is None:
        test_suite = get_tests(directories, specific_test)

    runner = TextTestRunner(verbosity=2, resultclass=MayaTestResult)
    runner.failfast = False
    runner.buffer = _config['params']['buffer_output']
    runner.run(test_suite)


def run_tests_from_command_line():
    """Runs tests in Maya standalone mode.

    This is called when running *src/main.py* from the command line.
    """
    from utils.standalone_context import MayaStandaloneContext

    with MayaStandaloneContext(mute_logger='userSetup'):
        run_tests(directories=_config['paths']['tests'] or [_config['default_tests']])


if __name__ == '__main__':
    run_tests_from_command_line()
