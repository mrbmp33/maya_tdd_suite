from qtpy import QtWidgets
from src.ui.maya_testing_ui import SettingsDialog, MayaTestRunnerDialog


def launch_ui():
    app = QtWidgets.QApplication([])
    widget = MayaTestRunnerDialog()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    launch_ui()
