import unittest


class TestResult(unittest.TextTestResult):
    """Customize the test result so we can do things like do a file new between each test and suppress script
    editor output.
    """
    def startTestRun(self):
        """Called before any tests are run."""
        super(TestResult, self).startTestRun()
        ScriptEditorState.suppress_output()
        if Settings.buffer_output:
            # Disable any logging while running tests. By disabling critical, we are disabling logging
            # at all levels below critical as well
            logging.disable(logging.CRITICAL)

    def stopTestRun(self):
        """Called after all tests are run."""
        if Settings.buffer_output:
            # Restore logging state
            logging.disable(logging.NOTSET)
        ScriptEditorState.restore_output()
        if Settings.delete_files and os.path.exists(Settings.temp_dir):
            shutil.rmtree(Settings.temp_dir)

        super(TestResult, self).stopTestRun()

    def stopTest(self, test):
        """Called after an individual test is run.

        @param test: TestCase that just ran."""
        super(TestResult, self).stopTest(test)
        if Settings.file_new:
            cmds.file(f=True, new=True)