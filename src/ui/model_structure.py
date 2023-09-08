import inspect
import traceback
import unittest
import pathlib
import logging
from typing import Collection, Tuple, List, Union

from qtpy import QtCore, QtGui
from enum import auto, IntEnum

from src.utils import config_loader, module_finder
from src import maya_test_case

_config = config_loader.load_config()
logger = logging.getLogger(__name__)
ICON_DIR = pathlib.Path(_config['paths']['icons'])


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

    def parent(self) -> "BaseTreeNode":
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

    found_icon = None
    success_icon = None
    fail_icon = None
    error_icon = None
    skip_icon = None

    @classmethod
    def set_states(cls):
        """This is to prevent a bug where QPixmap swallows errors."""

        # Hard-coded file names
        match_files_map = {
            'tdd_test_found': None,
            'tdd_test_success': None,
            'tdd_test_fail': None,
            'tdd_test_error': None,
            'tdd_test_skip': None,
        }

        icons_contents = ICON_DIR.iterdir()
        for f in icons_contents:
            if f.stem in match_files_map:
                match_files_map[f.stem] = str(f)

        cls.found_icon = QtGui.QIcon(QtGui.QPixmap(match_files_map['tdd_test_found']))
        cls.success_icon = QtGui.QIcon(QtGui.QPixmap(match_files_map['tdd_test_success']))
        cls.fail_icon = QtGui.QIcon(QtGui.QPixmap(match_files_map['tdd_test_fail']))
        cls.error_icon = QtGui.QIcon(QtGui.QPixmap(match_files_map['tdd_test_error']))
        cls.skip_icon = QtGui.QIcon(QtGui.QPixmap(match_files_map['tdd_test_skip']))

    def __init__(self, test, parent=None):
        super(TreeNode, self).__init__(parent)

        self.set_states()

        self.test_suite: Union[unittest.TestSuite, maya_test_case.MayaTestCase] = test
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
            # noinspection PyProtectedMember
            return self.test_suite._testMethodName
        elif isinstance(self.child(0).test_suite, unittest.TestCase):
            return self.child(0).test_suite.__class__.__name__
        else:
            return self.child(0).child(0).test_suite.__class__.__module__

    def path(self):
        """Gets the import path of the test.  Used for finding the test by name."""

        if isinstance(self.test_suite, unittest.TestSuite):
            for test in self.test_suite._tests:
                module_name = test.__class__.__module__
                yield "{0}.{1}.{2}".format(module_name, test.__class__.__name__, test._testMethodName)
        else:
            module_name = self.test_suite.__class__.__module__
            yield "{0}.{1}.{2}".format(module_name, self.test_suite.__class__.__name__, self.test_suite._testMethodName)

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
        x = 1
        return [
            None,
            TreeNode.found_icon,
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

        self.root_node = root
        self.node_lookup = {}

        # Create a lookup so that we can find the TestNode given a TestCase or TestSuite
        self.create_node_lookup(self.root_node)

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
            parent_node = self.root_node
        else:
            parent_node = parent.internalPointer()
        return parent_node.child_count()

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None
        node: TreeNode = index.internalPointer()
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
            if node.parent() is not self.root_node:
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
        if parent_node == self.root_node:
            return QtCore.QModelIndex()
        return self.createIndex(parent_node.row(), 0, parent_node)

    def index(self, row, column, parent):
        if not parent.isValid():
            parent_node = self.root_node
        else:
            parent_node = parent.internalPointer()

        child_item = parent_node.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QtCore.QModelIndex()

    def get_index_of_node(self, node):
        if node is self.root_node:
            return QtCore.QModelIndex()
        return self.index(node.row(), 0, self.get_index_of_node(node.parent()))

    def set_test_result_data(self, test_list: Collection[Tuple], status: TestStatus):
        """Store the test result data in model.

        Args:
            test_list: A list of tuples of test results.
            status: A TestStatus value.

        """
        for test, reason in test_list:
            node = self.node_lookup[str(test)]
            index = self.get_index_of_node(node)
            self.setData(index, reason, QtCore.Qt.ToolTipRole)
            self.setData(index, status, QtCore.Qt.DecorationRole)


def indices_to_tests(test_indexes: Collection[QtCore.QModelIndex]) -> List[str]:
    """Converts indexes into paths to tests."""

    # Remove any child nodes if parent nodes are in the list. This will prevent duplicate tests from being run.
    paths = []
    for index in test_indexes:
        node: TreeNode = index.internalPointer()
        paths.extend(list(node.path()))

    test_paths = []
    for path in paths:
        tokens = path.split(".")
        for i in range(len(tokens) - 1):
            p = ".".join(tokens[0: i + 1])
            if p in paths:
                break
        else:
            test_paths.append(path)
    return test_paths
