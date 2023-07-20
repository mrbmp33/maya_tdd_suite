from qtpy import QtWidgets, QtGui
from src.ui.maya_testing_ui import SettingsDialog, MayaTestRunnerWidget, TestsRunnerController


def launch_ui():
    app = QtWidgets.QApplication([])

    main_dialog = QtWidgets.QDialog()
    main_layout = QtWidgets.QVBoxLayout()
    main_layout.setContentsMargins(6, 6, 6, 6)
    main_dialog.setLayout(main_layout)
    main_dialog.setFixedSize(650, 400)

    # Add menu bar
    menu_bar = QtWidgets.QMenuBar()
    main_layout.setMenuBar(menu_bar)

    # Initialize inner widgets
    test_runner_widget = MayaTestRunnerWidget()
    settings_dialog = SettingsDialog(test_runner_widget)

    # Initialize controller default state
    controller = TestsRunnerController(settings_dialog.get_current_paths())
    controller.reload_model()

    # Change widget states
    test_runner_widget.tests_tree_view.setModel(controller.model)

    # Populate menu
    settings_action = QtGui.QAction('&Settings', main_dialog)
    # noinspection PyUnresolvedReferences
    settings_action.triggered.connect(settings_dialog.show)
    menu_bar.addAction(settings_action)

    # Add widgets to layout
    main_layout.addWidget(test_runner_widget)

    main_dialog.show()
    app.exec_()


if __name__ == '__main__':
    launch_ui()
