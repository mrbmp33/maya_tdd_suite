import os
import sys
from unittest import TextTestRunner, TestSuite, TestResult, TestLoader, TestCase
from typing import List

from utils import config_loader

_config = config_loader.load_config()


def add_to_path(path):
    """Add the specified path to the system path.

    @param path: Path to add.
    @return True if path was added. Return false if path does not exist or path was already in sys.path
    """
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)
        return True
    return False


# ==== TESTS COLLECTION ================================================================================================


def maya_module_tests():
    """Generator function to iterate over all the Maya module tests directories."""
    for path in os.environ['MAYA_MODULE_PATH'].split(os.pathsep):
        p = '{0}/tests'.format(path)
        if os.path.exists(p):
            yield p


def get_tests(directories: List[str] = None, specific_test: str = None, test_suite: TestSuite = None) -> TestSuite:
    """Get a *unittest.TestSuite* containing all the desired tests.

    Args:
        directories (List[str]): Optional list of directories with which to search for tests.  If omitted, use all
            "tests" directories of the modules found in the MAYA_MODULE_PATH.
        specific_test (str): Optional test path to find a specific test such as 'test_mytest.SomeTestCase.test_function'.
        test_suite (TestSuite): Optional unittest.TestSuite to add the discovered tests to.  If omitted a new TestSuite
            will be created.
    Returns:
         TestSuite: The populated TestSuite.
    """
    if directories is None:
        directories = maya_module_tests()

    # Populate a TestSuite with all the tests
    if test_suite is None:
        test_suite = TestSuite()

    if specific_test:
        # Find the specified test to run
        directories_added_to_path = [p for p in directories if add_to_path(p)]
        discovered_suite = TestLoader().loadTestsFromName(specific_test)
        if discovered_suite.countTestCases():
            test_suite.addTests(discovered_suite)
    else:
        # Find all tests to run
        directories_added_to_path = []
        for p in directories:
            discovered_suite = TestLoader().discover(p)
            if discovered_suite.countTestCases():
                test_suite.addTests(discovered_suite)

    # Remove the added paths.
    for path in directories_added_to_path:
        sys.path.remove(path)

    return test_suite


# ==== TEST EXECUTION ==================================================================================================


def run_tests(directories: List[str] = None, test: str = None, test_suite: TestSuite = None):
    """Run all the tests in the given paths.

    Args:
        directories (List[str]): A generator or list of paths containing tests to run.
        test (TestCase): Optional name of a specific test to run.
        test_suite (TestSuite): Optional TestSuite to run.  If omitted, a TestSuite will be generated.
    """

    if test_suite is None:
        test_suite = get_tests(directories, test)

    runner = TextTestRunner(verbosity=2, resultclass=TestResult)
    runner.failfast = False
    runner.buffer = _config['params']['buffer_output']
    runner.run(test_suite)


def run_tests_from_command_line():
    """Runs tests in Maya standalone mode.

    This is called when running *src/main.py* from the command line.
    """
    from utils.standalone_context import MayaStandalone

    with MayaStandalone():
        # Populate missing variables from mayapy's sys.path
        run_tests(directories=_config['paths']['tests'])


if __name__ == '__main__':
    run_tests_from_command_line()
