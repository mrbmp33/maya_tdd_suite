import logging
import unittest

import src.maya_test_case as maya_test

_logger = logging.getLogger("maya_tdd")
_logger.setLevel(logging.WARNING)


class OtherTestCase(maya_test.MayaTestCase):

    def test_passing(self):
        self.assertEqual(1, 1)

    @unittest.expectedFailure
    def test_failure(self):
        self.assertEqual(0, 1)

    def test_unexpected_failure(self):
        self.assertEqual(0, 1)


if __name__ == '__main__':
    unittest.main()
