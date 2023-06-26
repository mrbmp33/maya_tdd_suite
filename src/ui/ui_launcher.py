from qtpy import QtWidgets
from maya_testing_ui import SettingsDialog


def launch_ui():
    app = QtWidgets.QApplication([])
    widget = SettingsDialog()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    launch_ui()
