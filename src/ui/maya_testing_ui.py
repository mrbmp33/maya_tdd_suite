from typing import Optional
from pathlib import Path

from qtpy import QtWidgets, QtGui
from qtpy.uic import loadUi
from src.utils.config_loader import load_config, write_to_config

class TestsDirWidget(QtWidgets.QWidget):
    ...


class SettingsDialog(QtWidgets.QDialog):
    """Dialog that displays the settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tests_paths_wid: Optional[QtWidgets.QWidget] = None
        self.tests_paths_ls: Optional[QtWidgets.QListWidget] = None
        self.tmp_files_dir_le: Optional[QtWidgets.QLineEdit] = None
    
        self.buffer_output_cb: Optional[QtWidgets.QCheckBox] = None
        self.keep_tmp_files_cb: Optional[QtWidgets.QCheckBox] = None
        self.new_file_cb: Optional[QtWidgets.QCheckBox] = None
    
        # Initialize main layout and widget
        self.layout = QtWidgets.QVBoxLayout()
        self.main_widget = QtWidgets.QWidget()
        self.layout.setContentsMargins(9, 4, 9, 9)
    
        self.setLayout(self.layout)
        self.layout.addWidget(self.main_widget)
        
        # Load contents from ui file
        self._load_uis()
        
        # Load state from settings file
        self.load_settings()
    
    def load_settings(self):
        """Sets the state of the settings UI to be the same as the contents of the configuration file."""
        from src.utils.parsing_utils import resolve_env_variables_strings
        import os
        
        _config = load_config(resolve_vars=False)
        test_paths = set(_config['paths']['tests']) or [_config['default_tests']]
        resolved_tests_paths = [os.path.normpath(resolve_env_variables_strings(str(x))) for x in test_paths]
        
        # Tests directory
        self.tests_paths_ls.reset()
        for each in resolved_tests_paths:
            self.tests_paths_ls.addItem(each)
        
        # Tmp dir
        self.tmp_files_dir_le.setText(_config['paths']['tmp'])
        
        # Options
        self.buffer_output_cb.setChecked(_config['params']['buffer_output'])
        self.keep_tmp_files_cb.setChecked(_config['params']['keep_tmp_files'])
        self.new_file_cb.setChecked(_config['params']['file_new'])
    
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
                    'tests': [self.tests_paths_ls.item(index).text() for index in range(self.tests_paths_ls.count())],
                    'tmp': self.tmp_files_dir_le.text() or _config['default_tmp'],
                }
                
            }
        )
    
    def closeEvent(self, event: QtGui.QCloseEvent):
        self.save_settings()
        super().closeEvent(event)
        
    def _load_uis(self):
        loadUi(str(Path(__file__).parent / 'designer' / 'settings_widget.ui'), self)
        anchor_widget = self.findChild(QtWidgets.QWidget, 'tests_promote_wid')
        loadUi(str(Path(__file__).parent / 'designer' / 'tests_paths_widget.ui'),
            anchor_widget)
        
        self.tests_paths_wid = self.findChild(QtWidgets.QWidget, 'settings_wid')
        self.tests_paths_ls = self.findChild(QtWidgets.QListWidget, 'tests_paths_ls')
        

class MayaTestRunnerDialog(QtWidgets.QDialog):
    """Actual widget that will be implanted inside the base container for the UI.
    
    Best to keep it decoupled from maya code that is not ready to be mocked.
    """
    ...

    def __init__(self):
        super().__init__()


if __name__ == '__main__':
    ...
