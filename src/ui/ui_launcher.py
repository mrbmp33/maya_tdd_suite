from PySide6 import QtWidgets, QtGui
from src.ui.maya_testing_ui import SettingsDialog, TestsRunnerWidget, MayaTddDialog
from src.ui.controller import TestsRunnerController


def launch_ui():
    app = QtWidgets.QApplication([])

    maya_tdd_dialog = MayaTddDialog()

    # Initialize controller default state
    controller = TestsRunnerController(
        maya_tdd_dialog.settings_dialog.get_current_paths()
    )
    controller.reload_model()

    # Change widget states
    maya_tdd_dialog.test_runner_wid.tests_tree_view.setModel(controller.model)

    maya_tdd_dialog.show()
    app.exec_()


if __name__ == '__main__':
    launch_ui()
