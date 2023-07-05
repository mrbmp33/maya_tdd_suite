import os
from typing import Optional
from pathlib import Path
from qtpy import QtWidgets, QtGui, QtCore
from qtpy.uic import loadUi
from src.utils.config_loader import load_config, write_to_config


class TestsDirWidget(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)

        # Load from UI file
        loadUi(str(Path(__file__).parent / 'designer' / 'tests_paths_widget.ui'), self)

        self.paths_view: Optional[QtWidgets.QListView] = self.findChild(QtWidgets.QListView, 'tests_paths_ls')

        self.add_path_btn: Optional[QtWidgets.QPushButton] = None
        self.remove_path_btn: Optional[QtWidgets.QPushButton] = None

        self._make_button_connections()

    def set_model(self, model: QtCore.QAbstractListModel):
        self.paths_view.setModel(model)

    def _add_path(self):
        """Fires a file manager dialog and adds the selected path to the model's list."""
        if not self.paths_view.model():
            return

        # Fire file manager dialog
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

    # noinspection PyTypeChecker
    def _make_button_connections(self):
        self.add_path_btn: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'add_path_btn')
        self.remove_path_btn: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'remove_path_btn')

        self.add_path_btn.clicked.connect(self._add_path)
        self.remove_path_btn.clicked.connect(self._remove_path)


class SettingsDialog(QtWidgets.QDialog):
    """Dialog that displays the settings."""

    def __init__(self, parent=None, model: Optional[QtCore.QAbstractListModel] = None):
        super().__init__(parent)

        self.tests_paths_wid: Optional[TestsDirWidget] = None
        self.tests_paths_view: Optional[QtWidgets.QListView] = None
        self.tmp_files_dir_le: Optional[QtWidgets.QLineEdit] = None

        self.buffer_output_cb: Optional[QtWidgets.QCheckBox] = None
        self.keep_tmp_files_cb: Optional[QtWidgets.QCheckBox] = None
        self.new_file_cb: Optional[QtWidgets.QCheckBox] = None

        # Initialize main layout and widget
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_widget = QtWidgets.QWidget()
        self.main_layout.setContentsMargins(9, 4, 9, 9)
        self.setMinimumSize(500, 300)

        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.main_widget)

        # Load contents from ui file
        self._load_uis()

        # Load state from settings file
        self.load_settings()

    def _load_uis(self):
        loadUi(str(Path(__file__).parent / 'designer' / 'settings_widget.ui'), self)
        anchor_widget = self.findChild(QtWidgets.QWidget, 'tests_promote_wid')
        anchor_layout = QtWidgets.QVBoxLayout(anchor_widget)

        self.tests_paths_wid = TestsDirWidget()
        self.tests_paths_view = self.tests_paths_wid.findChild(QtWidgets.QListView, 'tests_paths_ls')

        anchor_layout.setContentsMargins(0, 0, 0, 0)
        anchor_layout.addWidget(self.tests_paths_wid)

    def set_model(self, model: QtCore.QAbstractListModel):
        """Sets the model of the nested TestsDirWidget."""
        self.tests_paths_wid.set_model(model)

    def load_settings(self):
        """Sets the state of the settings UI to be the same as the contents of the configuration file."""
        from src.utils.parsing_utils import resolve_env_variables_strings
        import os

        _config = load_config(resolve_vars=False)
        test_paths = set(_config['paths']['tests']) or [_config['default_tests']]
        resolved_tests_paths = [os.path.normpath(resolve_env_variables_strings(str(x))) for x in test_paths]
        resolved_tests_paths = sorted(list(filter(lambda x: os.path.exists(x), resolved_tests_paths)))

        # Tests directory
        self.set_model(QtCore.QStringListModel(resolved_tests_paths))

        # Tmp dir
        self.tmp_files_dir_le.setText(_config['paths']['tmp'])

        # Options
        self.buffer_output_cb.setChecked(_config['params']['buffer_output'])
        self.keep_tmp_files_cb.setChecked(_config['params']['keep_tmp_files'])
        self.new_file_cb.setChecked(_config['params']['file_new'])

    # ==== POST-START ==================================================================================================

    def save_settings(self):
        """Saves the UI state to the settings file."""

        _config = load_config(resolve_vars=False)

        write_to_config(
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


# ==== SETTINGS-RELATED UIS ============================================================================================


class MayaTestRunnerDialog(QtWidgets.QDialog):
    """Actual widget that will be implanted inside the base container for the UI.
    
    Best to keep it decoupled from maya code that is not ready to be mocked.
    """
    ...

    def __init__(self):
        super().__init__()
