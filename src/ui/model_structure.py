import traceback
import unittest
import pathlib
import os
import logging
from qtpy import QtCore, QtGui
from enum import auto, IntEnum

ICON_DIR = pathlib.Path(os.environ["MAYA_TDD_ROOT_DIR"]) / "icons"
logger = logging.getLogger(__name__)


class TestStatus(IntEnum):
    """Possible status codes of tests."""

    NOT_RUN = auto()
    SUCCESS = auto()
    FAIL = auto()
    ERROR = auto()
    SKIPPED = auto()


class BaseTreeNode:
    """Base tree node that contains hierarchical functionality for use in a QAbstractItemModel"""

    def __init__(self, parent=None):
        self.children = []
        self._parent = parent

        if parent is not None:
            parent.add_child(self)

    def add_child(self, child):
        """Add a child to the node.

        Args:
            child (BaseTreeNode): Child node to add."""
        if child not in self.children:
            self.children.append(child)

    def remove(self):
        """Remove this node and all its children from the tree."""
        if self._parent:
            row = self.row()
            self._parent.children.pop(row)
            self._parent = None
        for child in self.children:
            child.remove()

    def child(self, row):
        """Get the child at the specified index.

        Args:
            row: The child index.
        Returns:
            BaseTreeNode: The tree node at the given index or None if the index was out of bounds.
        """
        try:
            return self.children[row]
        except IndexError:
            return None

    def child_count(self):
        """Get the number of children in the node"""
        return len(self.children)

    def parent(self):
        """Get the parent of node"""
        return self._parent

    def row(self):
        """Get the index of the node relative to the parent"""
        if self._parent is not None:
            return self._parent.children.index(self)
        return 0

    def data(self, column):
        """Get the table display data"""
        return ""


# noinspection PyArgumentList
class TreeNode(BaseTreeNode):
    """A node representing a Test, TestCase, or TestSuite for display in a QTreeView. It can change its display based on
    the current state."""

    success_icon = None
    fail_icon = None
    error_icon = None
    skip_icon = None

    @classmethod
    def set_states(cls):
        """This is to prevent a bug where QPixmap swallows errors."""
        cls.success_icon = QtGui.QIcon(QtGui.QPixmap(str(ICON_DIR / "tdd_test_success.png")))
        cls.fail_icon = QtGui.QIcon(QtGui.QPixmap(str(ICON_DIR / "tdd_test_fail.png")))
        cls.error_icon = QtGui.QIcon(QtGui.QPixmap(str(ICON_DIR / "tdd_test_error.png")))
        cls.skip_icon = QtGui.QIcon(QtGui.QPixmap(str(ICON_DIR / "tdd_test_skip.png")))

    def __init__(self, test, parent=None):
        super(TreeNode, self).__init__(parent)

        self.set_states()

        self.test_suite = test
        self.tool_tip = str(test)
        self.status = TestStatus.NOT_RUN

        if isinstance(self.test_suite, unittest.TestSuite):
            for test_ in self.test_suite:
                if isinstance(test_, unittest.TestCase) or test_.countTestCases():
                    self.add_child(TreeNode(test_, self))

        if self.test_suite.__class__.__name__ == "ModuleImportFailure":
            try:
                getattr(self.test_suite, self.name())()
            except ImportError:
                self.tool_tip = traceback.format_exc()
                logger.warning(self.tool_tip)

    def name(self):
        """Get the name to print in the view."""
        if isinstance(self.test_suite, unittest.TestCase):
            return self.test_suite._testMethodName
        elif isinstance(self.child(0).test_suite, unittest.TestCase):
            return self.child(0).test_suite.__class__.__name__
        else:
            return self.child(0).child(0).test_suite.__class__.__module__

    def path(self):
        """Gets the import path of the test.  Used for finding the test by name."""
        if self.parent() and self.parent().parent():
            return "{0}.{1}".format(self.parent().path(), self.name())
        else:
            return self.name()

    def get_status(self) -> int:
        """Get the status of the TestNode.

        Nodes with children like the TestSuites, will get their status based on the
        status of the leaf nodes (the TestCases).

        Returns:
            A status value from TestStatus.
        """
        if "ModuleImportFailure" in [self.name(), self.test_suite.__class__.__name__]:
            return TestStatus.ERROR
        if not self.children:
            return self.status
        result = TestStatus.NOT_RUN
        for child in self.children:
            child_status = child.get_status()
            if child_status == TestStatus.ERROR:
                # Error status has the highest priority so propagate that up to the parent
                return child_status
            elif child_status == TestStatus.FAIL:
                result = child_status
            elif child_status == TestStatus.SUCCESS and result != TestStatus.FAIL:
                result = child_status
            elif child_status == TestStatus.SUCCESS and result != TestStatus.FAIL:
                result = child_status
        return result

    def get_icon(self):
        """Get the status icon to display with the Test."""
        status = self.get_status()
        return [
            None,
            TreeNode.success_icon,
            TreeNode.fail_icon,
            TreeNode.error_icon,
            TreeNode.skip_icon,
        ][status]


# noinspection PyMethodOverriding
class TestTreeModel(QtCore.QAbstractItemModel):
    """The model used to populate the test tree view."""

    def __init__(self, root, parent=None):
        super().__init__(parent)

        self._root_node = root
        self.node_lookup = {}

        # Create a lookup so that we can find the TestNode given a TestCase or TestSuite
        self.create_node_lookup(self._root_node)

    def create_node_lookup(self, node: TreeNode):
        """Create a lookup so that we can find the TestNode given a TestCase or TestSuite. The lookup will be used to
        set test statuses and tool tips after a test run.

        Parameters:
            node: Node to add to the map.
        """
        self.node_lookup[str(node.test_suite)] = node
        for child in node.children:
            self.create_node_lookup(child)

    def rowCount(self, parent):
        """Return the number of rows with this parent."""
        if not parent.isValid():
            parent_node = self._root_node
        else:
            parent_node = parent.internalPointer()
        return parent_node.child_count()

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return node.name()
        elif role == QtCore.Qt.DecorationRole:
            return node.get_icon()
        elif role == QtCore.Qt.ToolTipRole:
            return node.tool_tip

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        node = index.internalPointer()
        data_changed_kwargs = ([index, index, []])
        if role == QtCore.Qt.EditRole:
            self.dataChanged.emit(*data_changed_kwargs)
        if role == QtCore.Qt.DecorationRole:
            node.status = value
            self.dataChanged.emit(*data_changed_kwargs)
            if node.parent() is not self._root_node:
                self.setData(self.parent(index), value, role)
        elif role == QtCore.Qt.ToolTipRole:
            node.tool_tip = value
            self.dataChanged.emit(*data_changed_kwargs)

    def headerData(self, section, orientation, role):
        return "Tests"

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def parent(self, index):
        node = index.internalPointer()
        parent_node = node.parent()
        if parent_node == self._root_node:
            return QtCore.QModelIndex()
        return self.createIndex(parent_node.row(), 0, parent_node)

    def index(self, row, column, parent):
        if not parent.isValid():
            parent_node = self._root_node
        else:
            parent_node = parent.internalPointer()

        child_item = parent_node.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QtCore.QModelIndex()

    def get_index_of_node(self, node):
        if node is self._root_node:
            return QtCore.QModelIndex()
        return self.index(node.row(), 0, self.get_index_of_node(node.parent()))

    # def run_tests(self, stream, test_suite):
    #     """Runs the given TestSuite.
    #
    #     :param stream: A stream object with write functionality to capture the test output.
    #     :param test_suite: The TestSuite to run.
    #     """
    #     runner = unittest.TextTestRunner(
    #         stream=stream, verbosity=2, resultclass=mayaunittest.TestResult
    #     )
    #     runner.failfast = False
    #     runner.buffer = mayaunittest.Settings.buffer_output
    #     result = runner.run(test_suite)
    #
    #     self._set_test_result_data(result.failures, TestStatus.fail)
    #     self._set_test_result_data(result.errors, TestStatus.error)
    #     self._set_test_result_data(result.skipped, TestStatus.skipped)
    #
    #     for test in result.successes:
    #         node = self.node_lookup[str(test)]
    #         index = self.get_index_of_node(node)
    #         self.setData(index, "Test Passed", QtCore.Qt.ToolTipRole)
    #         self.setData(index, TestStatus.success, QtCore.Qt.DecorationRole)
    #
    # def _set_test_result_data(self, test_list, status):
    #     """Store the test result data in model.
    # S
    #     :param test_list: A list of tuples of test results.
    #     :param status: A TestStatus value."""
    #     for test, reason in test_list:
    #         node = self.node_lookup[str(test)]
    #         index = self.get_index_of_node(node)
    #         self.setData(index, reason, QtCore.Qt.ToolTipRole)
    #         self.setData(index, status, QtCore.Qt.DecorationRole)
