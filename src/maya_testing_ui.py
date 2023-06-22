from qtpy import QtWidgets


class MayaTestRunnerDialog(QtWidgets.QDialog):
    """Actual widget that will be implanted inside the base container for the UI.
    
    Best to keep it decoupled from maya code that is not ready to be mocked.
    """
    ...
