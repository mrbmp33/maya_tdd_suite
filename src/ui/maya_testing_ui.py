import os
from typing import Optional
from pathlib import Path
from qtpy import QtWidgets, QtGui, QtCore
from qtpy.uic import loadUi

from src.utils import reload_modules, config_loader, maya_locations
from src import run_tests
from . import model_structure


# ==== SETTINGS-RELATED UIS ============================================================================================

class TestsDirWidget(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)

        # Load from UI file
        loadUi(str(Path(__file__).parent / 'designer' / 'tests_paths_widget.ui'), self)

        # noinspection PyTypeChecker
        self.paths_view: Optional[QtWidgets.QListView] = self.findChild(QtWidgets.QListView, 'tests_paths_ls')
        self.add_path_btn: Optional[QtWidgets.QPushButton] = None
        self.remove_path_btn: Optional[QtWidgets.QPushButton] = None

        self._make_button_connections()

    def _add_path(self):
        """Fires a file manager dialog and adds the selected path to the model's list."""
        if not self.paths_view.model():
            return

        # Fire file manager dialog
        # noinspection PyArgumentList
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setDirectory(os.getenv('MAYA_TDD_ROOT_DIR', Path().cwd()))
        file_dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)

        model = self.paths_view.model()
        current_items = model.stringList()

        if file_dialog.exec_():
            selected_directory = file_dialog.selectedFiles()[0]
            current_items.append(selected_directory)
            model.setStringList(list(set(current_items)))

    def _remove_path(self):
        index = self.paths_view.selectedIndexes()
        if not index:
            return

        # Find the path stored in the selected index and remove it from the current state of the model
        model: QtCore.QStringListModel = self.paths_view.model()
        current_items: list = model.stringList()
        current_items.remove(index[0].data())

        model.setStringList(list(set(current_items)))

    # noinspection PyTypeChecker,PyUnresolvedReferences
    def _make_button_connections(self):
        self.add_path_btn: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'add_path_btn')
        self.remove_path_btn: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'remove_path_btn')

        self.add_path_btn.clicked.connect(self._add_path)
        self.remove_path_btn.clicked.connect(self._remove_path)

    # ==== GETTERS & SETTERS ===========================================================================================

    def set_model(self, model: QtCore.QAbstractListModel):
        self.paths_view.setModel(model)

    @property
    def model(self):
        return self.paths_view.model()

    @model.setter
    def model(self, model: QtCore.QAbstractListModel):
        """Sets the model of the nested TestsDirWidget."""
        self.paths_view.setModel(model)


class SettingsDialog(QtWidgets.QDialog):
    """Dialog that displays the settings."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.tests_paths_wid: Optional[TestsDirWidget] = None
        self.tests_paths_view: Optional[QtWidgets.QListView] = None
        self.tmp_files_dir_le: Optional[QtWidgets.QLineEdit] = None

        self.buffer_output_cb: Optional[QtWidgets.QCheckBox] = None
        self.keep_tmp_files_cb: Optional[QtWidgets.QCheckBox] = None
        self.new_file_cb: Optional[QtWidgets.QCheckBox] = None

        # Initialize main layout and widget
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_widget = QtWidgets.QWidget(self)
        self.main_layout.setContentsMargins(9, 4, 9, 9)
        # noinspection PyArgumentList
        self.setMinimumSize(500, 300)

        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.main_widget)

        # Load contents from ui file
        self._load_uis()

        # Load state from settings file
        self.load_settings()

    def _load_uis(self):
        loadUi(str(Path(__file__).parent / 'designer' / 'settings_widget.ui'), self)

        # noinspection PyTypeChecker
        anchor_widget: QtWidgets.QWidget = self.findChild(QtWidgets.QWidget, 'tests_promote_wid')
        anchor_layout = QtWidgets.QVBoxLayout()
        anchor_widget.setLayout(anchor_layout)

        self.tests_paths_wid = TestsDirWidget()
        self.tests_paths_view = self.tests_paths_wid.findChild(QtWidgets.QListView, 'tests_paths_ls')

        anchor_layout.setContentsMargins(0, 0, 0, 0)
        anchor_layout.addWidget(self.tests_paths_wid)

    def load_settings(self):
        """Sets the state of the settings UI to be the same as the contents of the configuration file."""
        from src.utils.parsing_utils import resolve_env_variables_strings
        import os

        _config = config_loader.load_config(resolve_vars=False)
        test_paths = set(_config['paths']['tests']) or [_config['default_tests']]
        resolved_tests_paths = [os.path.normpath(resolve_env_variables_strings(str(x))) for x in test_paths]
        resolved_tests_paths = sorted(list(filter(lambda x: os.path.exists(x), resolved_tests_paths)))

        # Tests directory
        self.model = QtCore.QStringListModel(resolved_tests_paths)

        # Tmp dir
        self.tmp_files_dir_le.setText(_config['paths']['tmp'])

        # Options
        self.buffer_output_cb.setChecked(_config['params']['buffer_output'])
        self.keep_tmp_files_cb.setChecked(_config['params']['keep_tmp_files'])
        self.new_file_cb.setChecked(_config['params']['file_new'])

    # ==== POST-START ==================================================================================================

    def save_settings(self):
        """Saves the UI state to the settings file."""

        _config = config_loader.load_config(resolve_vars=False)

        config_loader.write_to_config(
            {
                'params': {
                    'buffer_output': self.buffer_output_cb.isChecked(),
                    'keep_tmp_files': self.keep_tmp_files_cb.isChecked(),
                    'file_new': self.new_file_cb.isChecked(),
                },
                'paths': {
                    'tests': self.tests_paths_view.model().stringList(),
                    'tmp': self.tmp_files_dir_le.text() or _config['default_tmp'],
                }

            }
        )

    def closeEvent(self, event: QtGui.QCloseEvent):
        self.save_settings()
        super().closeEvent(event)

    # ==== Get info ====================================================================================================

    def get_current_paths(self) -> list:
        return self.model.stringList()

    @property
    def model(self):
        return self.tests_paths_wid.model

    @model.setter
    def model(self, model: QtCore.QAbstractListModel):
        """Sets the model of the nested TestsDirWidget."""
        self.tests_paths_wid.model = model


# ==== MAIN UI DEFINITION ==============================================================================================

class TestsRunnerController:
    """In charge of manipulating the model."""

    instance = None

    def __new__(cls, *args, **kwargs):
        """Singleton to ensure only one controller exists at a time."""
        if not isinstance(cls.instance, cls):
            cls.instance = super().__new__(cls)

        return cls.instance

    def __init__(self, test_directories: Optional[list] = None):

        self.model: Optional[QtCore.QAbstractItemModel] = None
        self.test_directories = test_directories

        # Take a snapshot of the currently-loaded modules to revert to this state after code execution
        self.rollback_importer = reload_modules.RollbackImporter()

        # Initialize the necessary environment variables
        maya_locations.set_maya_env_variables()

    def reload_model(self):
        """Re-inspects all the directories looking for new tests to run and reloads the latest version of the code."""
        self.reset_rollback_importer()
        for path in self.test_directories:
            run_tests.add_to_path(reload_modules.find_importable_root(path))

        test_suite = run_tests.get_tests(self.test_directories or None)

        # Reset model population
        root_node = model_structure.TreeNode(test_suite)
        self.model = model_structure.TestTreeModel(root_node)

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


class MayaTestRunnerWidget(QtWidgets.QWidget):
    """Actual widget that will be implanted inside the base container for the UI.
    
    Best to keep it decoupled from maya code that is not ready to be mocked.
    """

    # noinspection PyArgumentList
    def __init__(self, parent=None, *args, **kwargs):
        super(MayaTestRunnerWidget, self).__init__(parent=parent, *args, **kwargs)

        self.controller: Optional[TestsRunnerController] = None

        self.run_all_btn: Optional[QtWidgets.QPushButton] = None
        self.run_selected_btn: Optional[QtWidgets.QPushButton] = None
        self.run_failed_btn: Optional[QtWidgets.QPushButton] = None

        self.tests_tree_view: Optional[QtWidgets.QTreeView] = None

        loadUi(str(Path(__file__).parent / 'designer' / 'tests_runner_widget.ui'), self)

        # Add icons to buttons
        self.run_all_btn.setIcon(QtGui.QIcon(QtGui.QPixmap(
            str(Path(os.environ['MAYA_TDD_ROOT_DIR']) / 'icons' / 'tdd_run_all_tests.png'))))
        self.run_selected_btn.setIcon(QtGui.QIcon(QtGui.QPixmap(
            str(Path(os.environ['MAYA_TDD_ROOT_DIR']) / 'icons' / 'tdd_run_selected_tests.png'))))
        self.run_failed_btn.setIcon(QtGui.QIcon(QtGui.QPixmap(
            str(Path(os.environ['MAYA_TDD_ROOT_DIR']) / 'icons' / 'tdd_run_failed_tests.png'))))

    def expand_tree(self):
        """Manage Tree view"""
        ...
