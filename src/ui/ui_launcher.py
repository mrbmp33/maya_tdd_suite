from qtpy import QtWidgets, QtCore
from src.ui.maya_testing_ui import SettingsDialog, TestsRunnerWidget, MayaTddDialog
from src.ui.controller import TestsRunnerController


def launch_ui():
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication([])

    controller = TestsRunnerController()
    maya_tdd_dialog = MayaTddDialog(controller)

    # Initialize controller default state
    controller.test_directories = maya_tdd_dialog.settings_dialog.get_current_paths()

    # Change widget states
    maya_tdd_dialog.test_runner_wid.tests_tree_view.setModel(controller.model)
    maya_tdd_dialog.test_runner_wid.expand_tree(controller.model.root_node)

    maya_tdd_dialog.show()
    app.exec_()


if __name__ == '__main__':
    launch_ui()
