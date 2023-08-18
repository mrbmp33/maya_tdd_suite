"""Module that contains the object that operates with the data inside the UI's model."""

from typing import Optional, Collection

from qtpy import QtCore

from src import run_tests
from src.ui import model_structure
from src.utils import reload_modules, maya_locations


class TestsRunnerController:
    """In charge of manipulating the model from outside it."""

    instance = None

    def __new__(cls, *args, **kwargs):
        """Singleton to ensure only one controller exists at a time."""
        if not isinstance(cls.instance, cls):
            cls.instance = super().__new__(cls)

        return cls.instance

    def __init__(self, test_directories: Optional[list] = None):

        self.model: Optional[QtCore.QAbstractItemModel] = None
        self._test_directories = test_directories

        # Take a snapshot of the currently-loaded modules to revert to this state after code execution
        self.rollback_importer = reload_modules.RollbackImporter()

        # Initialize the necessary environment variables
        maya_locations.set_maya_env_variables()

    def reload_model(self):
        """Re-inspects all the directories looking for new tests to run and reloads the latest version of the code."""
        self.reset_rollback_importer()

        for path in self.test_directories:
            run_tests.add_to_path(path)

        test_suite = run_tests.get_tests(self._test_directories or None)

        # Reset model population
        root_node = model_structure.TreeNode(test_suite)
        self.model = model_structure.TestTreeModel(root_node)

    @property
    def test_directories(self):
        return self._test_directories

    @test_directories.setter
    def test_directories(self, new_dirs: Collection):
        """Sets and triggers the model update."""
        self._test_directories = new_dirs
        self.reload_model()

    # ==== RUNNING TESTS ===============================================================================================

    def run_all_tests(self):
        ...

    def run_selected_tests(self, indices):
        ...

    def run_failed_tests(self):
        ...

    def reset_rollback_importer(self):
        """Resets the RollbackImporter which allows the test runner to pick up code updates without having to reload
        anything."""

        if self.rollback_importer:
            self.rollback_importer.uninstall()

        # Create a new rollback importer to pick up any code updates
        self.rollback_importer = reload_modules.RollbackImporter()
