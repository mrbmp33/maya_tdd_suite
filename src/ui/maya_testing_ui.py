import logging
import os
from pathlib import Path
from typing import Optional

from qtpy import QtWidgets, QtGui, QtCore
from qtpy.uic import loadUi

from src.utils import config_loader
from src.ui.controller import TestsRunnerController
from src.ui.model_structure import TreeNode
from src.ui import output_console

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


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
        file_dialog.setReadOnly(True)
        file_dialog.setNameFilter("Python Files (*.py);;All Files (*)")

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

    updated_settings_signal = QtCore.Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.tests_paths_wid: Optional[TestsDirWidget] = None
        self.tests_paths_view: Optional[QtWidgets.QListView] = None
        self.tmp_files_dir_le: Optional[QtWidgets.QLineEdit] = None

        self.buffer_output_cb: Optional[QtWidgets.QCheckBox] = None
        self.keep_tmp_files_cb: Optional[QtWidgets.QCheckBox] = None
        self.new_file_cb: Optional[QtWidgets.QCheckBox] = None

        # Load contents from ui file
        self._load_uis()

        # Load state from settings file
        self.load_settings()

    def _load_uis(self):
        # Initialize main layout and widget
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_widget = QtWidgets.QWidget(self)
        self.main_layout.setContentsMargins(9, 4, 9, 9)
        # noinspection PyArgumentList
        self.setMinimumSize(500, 300)

        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.main_widget)

        # Load contents from ui file
        loadUi(str(Path(__file__).parent / 'designer' / 'settings_widget.ui'), self)

        # noinspection PyTypeChecker
        anchor_widget: QtWidgets.QWidget = self.findChild(QtWidgets.QWidget, 'tests_promote_wid')
        anchor_layout = QtWidgets.QVBoxLayout()
        anchor_widget.setLayout(anchor_layout)

        self.tests_paths_wid = TestsDirWidget()
        self.tests_paths_view = self.tests_paths_wid.findChild(QtWidgets.QListView, 'tests_paths_ls')

        anchor_layout.setContentsMargins(0, 0, 0, 0)
        anchor_layout.addWidget(self.tests_paths_wid)

        # Load state from settings file
        self.load_settings()

    # ==== POST-START ==================================================================================================

    def save_settings(self):
        """Saves the UI state to the settings file."""

        _config = config_loader.load_config(resolve_vars=False)

        new_paths = {
            'tests': self.tests_paths_view.model().stringList(),
            'tmp': self.tmp_files_dir_le.text() or _config['default_tmp'],
        }
        new_paths.update(_config['paths'])

        out_dict = {
            'params': {
                'buffer_output': self.buffer_output_cb.isChecked(),
                'keep_tmp_files': self.keep_tmp_files_cb.isChecked(),
                'file_new': self.new_file_cb.isChecked(),
            },
            'paths': new_paths,
        }

        config_loader.write_to_config(out_dict)

    def closeEvent(self, event: QtGui.QCloseEvent):
        self.save_settings()
        self.updated_settings_signal.emit(self.get_current_paths())
        super().closeEvent(event)

    # ==== GET INFO ====================================================================================================

    def get_current_paths(self) -> list:
        return self.model.stringList()

    @property
    def model(self):
        return self.tests_paths_wid.model

    @model.setter
    def model(self, model: QtCore.QAbstractListModel):
        """Sets the model of the nested TestsDirWidget."""
        self.tests_paths_wid.model = model

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


# ==== UI DEFINITION ===================================================================================================


# noinspection PyArgumentList
class TestsRunnerWidget(QtWidgets.QWidget):
    """Actual widget that will be implanted inside the base container for the UI.
    
    Best to keep it decoupled from maya code that is not ready to be mocked.
    """

    def __init__(self, parent=None, controller=None, *args, **kwargs):
        super(TestsRunnerWidget, self).__init__(parent=parent, *args, **kwargs)

        self.controller: Optional[TestsRunnerController] = controller

        self.splitter = None
        self.console_parent_wid: Optional[QtWidgets.QWidget] = None
        self.run_all_btn: Optional[QtWidgets.QPushButton] = None
        self.run_selected_btn: Optional[QtWidgets.QPushButton] = None
        self.run_failed_btn: Optional[QtWidgets.QPushButton] = None

        self.tests_tree_view: Optional[QtWidgets.QTreeView] = None
        self.output_console = output_console.OutputConsole()

        # Initialize elements
        self.__init_ui()

    def __init_ui(self):
        """Loads the UI components."""

        # Main layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        # Actions bar
        self.buttons_bar = QtWidgets.QMenuBar()
        main_layout.addWidget(self.buttons_bar)
        self.__actions_setup()

        # Load from file
        loadUi(str(Path(__file__).parent / 'designer' / 'tests_runner_widget.ui'), self)

        self.splitter.setStretchFactor(1, 4)

        # Insert the output console inside the loaded UI
        self.output_console.setParent(self.console_parent_wid)
        self.console_parent_wid.layout().addWidget(self.output_console)
        self.output_console.add_color("^ok", 92, 184, 92)
        self.output_console.add_color("^FAIL", 240, 173, 78)
        self.output_console.add_color("^ERROR", 217, 83, 79)
        self.output_console.add_color("^skipped", 88, 165, 204)

        # Set the tree view selection mode
        self.tests_tree_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def __actions_setup(self):
        """Defines and initializes the actions used to run tests."""

        # Run all tests
        run_all = self.buttons_bar.addAction("Run All Tests")
        run_all.setIcon(QtGui.QIcon(QtGui.QPixmap(
            str(Path(os.environ['MAYA_TDD_ROOT_DIR']) / 'icons' / 'tdd_run_all_tests.png')))
        )
        run_all.setToolTip("Run all tests.")

        # Run selected tests only
        run_selected = self.buttons_bar.addAction("Run Selected Tests")
        run_selected.setIcon(QtGui.QIcon(QtGui.QPixmap(
            str(Path(os.environ['MAYA_TDD_ROOT_DIR']) / 'icons' / 'tdd_run_selected_tests.png')))
        )
        run_selected.setToolTip("Run all selected tests.")

        # Run failed tests
        run_failed = self.buttons_bar.addAction("Run Failed Tests")
        run_failed.setIcon(QtGui.QIcon(QtGui.QPixmap(
            str(Path(os.environ['MAYA_TDD_ROOT_DIR']) / 'icons' / 'tdd_run_failed_tests.png')))
        )
        run_failed.setToolTip("Run all failed tests.")

        # If the widget has a controller attached, connect the actions to it
        if self.controller:
            run_all.triggered.connect(self.__run_all_tests_cb)
            run_selected.triggered.connect(self.__run_selected_tests_cb)
            run_failed.triggered.connect(self.__run_failed_tests_cb)

    # ==== VISUALIZATION ===============================================================================================

    def expand_tree(self, node: TreeNode):
        """Expands all the collapsed elements in a tree starting at the root_node."""

        parent = node.parent()
        model: QtCore.QAbstractItemModel = self.tests_tree_view.model()

        parent_idx = (model.createIndex(parent.row(), 0, parent) if parent else QtCore.QModelIndex())
        index = model.index(node.row(), 0, parent_idx)

        self.tests_tree_view.setExpanded(index, True)

        for child in node.children:
            self.expand_tree(child)

    # ==== CLEANUP CALLBACKS ===========================================================================================

    def __run_all_tests_cb(self):
        """Cleans the console and runs all tests."""
        self.output_console.clear()
        self.controller.run_all_tests(self.output_console)

    def __run_selected_tests_cb(self):
        """Cleans the console and runs selected tests."""
        self.output_console.clear()
        self.controller.run_selected_tests(self.output_console)

    def __run_failed_tests_cb(self):
        """Cleans the console and runs only the failed tests."""
        self.output_console.clear()
        self.controller.run_failed_tests(self.output_console)


class MayaTddDialog(QtWidgets.QDialog):
    DEFAULT_SIZE = (1000, 900)

    def __init__(self, controller: TestsRunnerController, parent=None):
        super().__init__(parent)

        # Window must have some controller
        self.controller = controller

        self.setBaseSize(*self.__class__.DEFAULT_SIZE)
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(6, 6, 6, 6)

        # Initialize inner widgets
        self.test_runner_wid = TestsRunnerWidget(parent=self, controller=controller)
        self.settings_dialog = SettingsDialog(self)

        # Add menu bar
        self.menu_bar = QtWidgets.QMenuBar()
        main_layout.setMenuBar(self.menu_bar)

        main_layout.addWidget(self.test_runner_wid)
        self.setLayout(main_layout)

        self._setup_actions()
        self._make_connections()

    def _setup_actions(self):
        """Creates and links actions to operate with the inner widgets."""

        # Action for launching paths dialog from settings menu
        settings_action = QtGui.QAction('&Settings', self)
        # noinspection PyUnresolvedReferences
        settings_action.triggered.connect(self.settings_dialog.open)
        self.menu_bar.addAction(settings_action)

    def _make_connections(self):
        """Links the controller and the settings dialog."""
        self.settings_dialog.updated_settings_signal.connect(self._update_model)
        self.settings_dialog.updated_settings_signal.connect(self._reset_output)

    @QtCore.Slot(list)
    def _reset_output(self):
        self.test_runner_wid.output_console.clear()

    @QtCore.Slot(list)
    def _update_model(self, paths: list):
        _logger.debug('Updating model data.')
        self.controller.test_directories = paths
        self.test_runner_wid.tests_tree_view.setModel(self.controller.model)
        self.test_runner_wid.expand_tree(self.controller.model.root_node)
