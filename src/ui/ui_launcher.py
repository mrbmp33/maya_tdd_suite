from qtpy import QtWidgets
from src.ui.maya_testing_ui import SettingsDialog, MayaTestRunnerDialog, TestsRunnerController


def launch_ui():
    app = QtWidgets.QApplication([])

    widget = MayaTestRunnerDialog()
    controller = TestsRunnerController()

    widget.tests_tree_view.setModel(controller.model)

    widget.show()
    app.exec_()


if __name__ == '__main__':
    launch_ui()
