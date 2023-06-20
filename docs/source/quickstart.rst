Configuration Variables
=======================

These should be set by interacting with the UI. Here's what they do.

- params:
    - keep_tmp_files (True): Either if you want to preserve the tmp files after each test execution.
    - buffer_output (True): If you want to display the output of the tests at the end or inbetween tests.

    paths:
      default_tests: Default directory to find tests. It points to this package by default, but not necessarily.
      tests: All directories that will be inspected to find tests.
      tmp: Temporary location for files that get generated from tests and must be deleted after the execution.

You can use environment variables for setting these values by using the following syntax:

.. code-block:: regex

    $ENV{YOUR_VAR}here_you_are_free_to_user_whatever_you_want