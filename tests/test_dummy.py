import logging
import unittest
import pathlib
import os

import src.maya_test_case as maya_test
from utils import config_loader

_config = config_loader.load_config()
_logger = logging.getLogger("maya_tdd")
_logger.setLevel(logging.WARNING)


class DummyTestCase(maya_test.MayaTestCase):

    def test_get_tmp_file_name(self):
        """Generate a bunch of temporary files to test that the naming convention persists."""

        # Get the initial length of files created to compare with the ending one
        len_to_delete_init = len(self.__class__.files_created)

        uuid = 'hi'

        # Get the file name from the file name builder. This will also create the tmp dir.
        tmp_file_name = pathlib.Path(self.get_temp_filename(f"{uuid}.log"))

        max_iterations = 10

        num = 0

        while num <= max_iterations:
            expected_file_name = pathlib.Path(_config["paths"]["tmp"]) / f"{uuid}.{num}.log"

            try:
                # Expected to break if the file already exists
                expected_file_name.touch(exist_ok=False)

                self.assertEqual(expected_file_name, tmp_file_name)
                self.assertGreater(len(self.__class__.files_created), len_to_delete_init)

                return

            except OSError:
                _logger.debug(f"File: {expected_file_name} already exists. Incrementing name...")
                num += 1

        # _logger.warning("There were more leftover files in the tmp dir than the max iterations to test. You should"
        #                 "consider cleaning them up.")

    def test_some_other_thing(self):
        self.assertTrue(True)


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
