import os
import shutil
import unittest
from dataclasses import dataclass
from typing import Optional
import logging
from utils.config_loader import load_config
import maya.cmds as mc

_config = load_config()


@dataclass
class ScriptEditorState:
    SUPRESS_RESULTS: Optional[bool] = None
    SUPRESS_ERRORS: Optional[bool] = None
    SUPRESS_WARNINGS: Optional[bool] = None
    SUPRESS_INFO: Optional[bool] = None
    
    @classmethod
    def suppress_output(cls):
        """Hides all script editor output."""
        if _config['params']['buffer_output']:
            cls.SUPRESS_RESULTS = mc.scriptEditorInfo(q=True, suppressResults=True)
            cls.SUPRESS_ERRORS = mc.scriptEditorInfo(q=True, suppressErrors=True)
            cls.SUPRESS_WARNINGS = mc.scriptEditorInfo(q=True, suppressWarnings=True)
            cls.SUPRESS_INFO = mc.scriptEditorInfo(q=True, suppressInfo=True)
            mc.scriptEditorInfo(
                e=True,
                suppressResults=True,
                suppressInfo=True,
                suppressWarnings=True,
                suppressErrors=True,
            )

    @classmethod
    def restore_output(cls):
        """Restores the script editor output settings to their original values."""
        if None not in {
            cls.SUPRESS_RESULTS,
            cls.SUPRESS_ERRORS,
            cls.SUPRESS_WARNINGS,
            cls.SUPRESS_INFO,
        }:
            mc.scriptEditorInfo(
                e=True,
                suppressResults=cls.SUPRESS_RESULTS,
                suppressInfo=cls.SUPRESS_INFO,
                suppressWarnings=cls.SUPRESS_WARNINGS,
                suppressErrors=cls.SUPRESS_ERRORS,
            )


class MayaTestResult(unittest.TextTestResult):
    """Customize the test result, so we can do things like do a file new between each test and suppress script
    editor output.
    """

    successes = []

    def addSuccess(self, test: unittest.case.TestCase) -> None:
        """Manually keep track of successes."""
        super(MayaTestResult, self).addSuccess(test)
        self.successes.append((test, "Success"))

    def startTestRun(self):
        """Called before any tests are run."""
        super(MayaTestResult, self).startTestRun()
        
        ScriptEditorState.suppress_output()
        if _config['params']['buffer_output']:
            # Disable any logging while running tests. By disabling critical, we are disabling logging
            # at all levels below critical as well
            logging.disable(logging.CRITICAL)
    
    def stopTestRun(self):
        """Called after all tests are run."""
        if _config['params']['buffer_output']:
            # Restore logging state
            logging.disable(logging.NOTSET)
            
        ScriptEditorState.restore_output()
        
        settings_dir = _config['paths']['tmp']
        if _config['params']['keep_tmp_files'] and os.path.exists(settings_dir):
            shutil.rmtree(settings_dir)
        
        super(MayaTestResult, self).stopTestRun()
    
    def stopTest(self, test):
        """Called after an individual test is run.

        @param test: TestCase that just ran."""
        super(MayaTestResult, self).stopTest(test)
        if _config['params']['file_new']:
            mc.file(f=True, new=True)
