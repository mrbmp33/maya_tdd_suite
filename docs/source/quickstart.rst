Configuration Variables
=======================

These should be set by interacting with the UI. Here's what they do.

- params:
    - keep_tmp_files (True): Either if you want to preserve the tmp files after each test execution.
    - buffer_output (True): If you want to display the output of the tests at the end or inbetween tests.
    - new_file (True): Whether or not you want to create a new file before running a test.

- paths:
    - default_tests (str): Default directory to find tests. It points to this package by default, but not necessarily.
    - tests (list): All directories that will be inspected to find tests.
    - tmp (str): Temporary location for files that get generated from tests and must be deleted after the execution.

You can use environment variables for setting these values by using the following syntax:

.. code-block:: regex

    $ENV{YOUR_VAR}here_you_are_free_to_user_whatever_you_want


Which tests will it be executed?
================================

The tests that will run will be those that the inspection is able to find in a given set of paths.

Primarily, the inspection will look for tests inside the "['paths']['tests']" configuration value. This value is a list
and can be set either manually or through the application's UI.

Alternatively, you can also create subfolders of the paths set in your 'MAYA_MODULE_PATH' environment variable named
tests like the following:

<my/awesome/path/tests>

Just keep in mind that if the variable has not previously been set it will fallback to use this project's </tests> directory.


Launching tests from the command line
-------------------------------------

If you are launching the tests from the terminal, call the "main.py" file under <src>. This will execute all the tests
located under the project's */tests* directory.

..todo: Should probably add the functionality to pass paths as an argument when launching tests from the cmd line.
