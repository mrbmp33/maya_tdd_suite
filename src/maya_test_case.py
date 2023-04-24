"""Module that contains a class to inherit from in order to create Maya tests.

Credits to Chad Vernon's and :ref:`his guide to crating a testing framework for Maya
<https://www.chadvernon.com/blog/unit-testing-in-maya/>`_. """

import unittest
import os
import maya.cmds as mc
import pathlib

import config_loader

_config = config_loader.load_config()


class MayaTestCase(unittest.TestCase):
    """Abstract class for creating tests for Maya.
    
    It contains utility methods for managing custom plugins and creating/deleting temp files.
    """
    
    # Keep track of all temporary files that were created, so they can be cleaned up after
    # all tests have been run
    files_created = []
    
    # Keep track of which plugins were loaded, so we can unload them after all tests have been run
    plugins_loaded = set()
    
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        
        cls.delete_temp_files()
        cls.unload_plugins()
    
    # ==== INITIALIZE / UNLOAD PLUGINS =================================================================================
    
    @classmethod
    def load_plugin(cls, plugin):
        """Load the given plug-in and saves it to be unloaded when the TestCase is finished.

        Args:
            plugin (str): Plug-in name.
        """
        
        mc.loadPlugin(plugin, qt=True)
        cls.plugins_loaded.add(plugin)
    
    @classmethod
    def unload_plugins(cls):
        # Unload any plugins that this test case loaded
        
        for plugin in cls.plugins_loaded:
            mc.unloadPlugin(plugin)
        cls.plugins_loaded = []
    
    # ===== FILE MANAGEMENT ============================================================================================
    
    @classmethod
    def delete_temp_files(cls):
        """Delete the temp files in the cache and clear the cache."""
        
        if _config["KEEP_TMP_FILES"]:
            for f in cls.files_created:
                if os.path.exists(f):
                    os.remove(f)
            cls.files_create = []

    @classmethod
    def get_temp_filename(cls, file_name):
        """Get a unique filepath name in the testing directory.

        The file will not be created, that is up to the caller.  This file will be deleted when
        the tests are finished.
        @param file_name: A partial path ex: 'directory/some_file.txt'
        @return The full path to the temporary file.
        """
        temp_dir = _config["MAYA_TDD_TMP_DIR"]
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        base_name, ext = os.path.splitext(file_name)
        path = '{0}/{1}{2}'.format(temp_dir, base_name, ext)
        count = 0
        while os.path.exists(path):
            # If the file already exists, add an incremented number
            count += 1
            path = '{0}/{1}{2}{3}'.format(temp_dir, base_name, count, ext)
        cls.files_created.append(path)
        return path
