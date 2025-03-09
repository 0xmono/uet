import unittest
import os
import json
import tempfile
import logging
from unittest.mock import patch, MagicMock
from ue.project import (
    split_build_name, get_plugins, create_build_name, 
    get_target_from_build_name, has_build_target,
    get_build_targets, update_plugins_by_project_file,
    get_engine_id, get_engine_root_path
)

class TestProject(unittest.TestCase):
    def setUp(self):
        # Suppress logging during tests
        logging.disable(logging.CRITICAL)
        
    def tearDown(self):
        # Re-enable logging
        logging.disable(logging.NOTSET)
        
    def test_split_build_name(self):
        test_cases = [
            ("MyProjectEditor", ("MyProject", "Editor")),
            ("MyProject", ("MyProject", "Game")),
            ("MyProjectClient", ("MyProject", "Client")),
            ("MyProjectServer", ("MyProject", "Server")),
            # Edge cases
            ("Editor", ("Editor", "Game")),  # Project named "Editor"
            ("EditorEditor", ("Editor", "Editor")),  # Project named "Editor" with Editor target
            ("", None),  # Empty string
        ]
        
        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = split_build_name(input_name)
                self.assertEqual(result, expected)

    def test_create_build_name(self):
        test_cases = [
            ("MyProject", "Editor", "MyProjectEditor"),
            ("MyProject", "Game", "MyProject"),
            ("MyProject", "Client", "MyProjectClient"),
            ("MyProject", "Server", "MyProjectServer"),
            # Case sensitivity tests
            ("MyProject", "editor", "MyProjectEditor"),
            ("MyProject", "game", "MyProject"),
        ]
        
        for project_name, target, expected in test_cases:
            with self.subTest(project_name=project_name, target=target):
                result = create_build_name(project_name, target)
                self.assertEqual(result, expected)

    def test_get_target_from_build_name(self):
        test_cases = [
            ("MyProjectEditor", "MyProject", "Editor"),
            ("MyProject", "MyProject", "Game"),
            ("MyProjectClient", "MyProject", "Client"),
            ("MyProjectServer", "MyProject", "Server"),
        ]
        
        for build_name, project_name, expected in test_cases:
            with self.subTest(build_name=build_name, project_name=project_name):
                result = get_target_from_build_name(build_name, project_name)
                self.assertEqual(result, expected)

    def test_get_plugins(self):
        # Create a temporary project file
        test_project_data = {
            "Plugins": [
                {"Name": "TestPlugin1", "Enabled": "true"},
                {"Name": "TestPlugin2", "Enabled": "false"},
                {"Name": "TestPlugin3", "Enabled": "invalid"},  # Invalid value
                {"InvalidPlugin": "No name field"}  # Missing name field
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.uproject') as tf:
            json.dump(test_project_data, tf)
            temp_path = tf.name
            
        try:
            # Test reading plugins
            plugins = get_plugins(temp_path)
            
            self.assertEqual(len(plugins), 3)
            self.assertTrue(plugins["TestPlugin1"]["Enabled"])
            self.assertFalse(plugins["TestPlugin2"]["Enabled"])
            self.assertFalse(plugins["TestPlugin3"]["Enabled"])  # Should default to False for invalid
            
        finally:
            # Cleanup
            os.unlink(temp_path)
            
    def test_get_plugins_invalid_file(self):
        # Test with non-existent file
        plugins = get_plugins("non_existent_file.uproject")
        self.assertEqual(plugins, {})
        
        # Test with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.uproject') as tf:
            tf.write("{ invalid json")
            temp_path = tf.name
            
        try:
            plugins = get_plugins(temp_path)
            self.assertEqual(plugins, {})
        finally:
            os.unlink(temp_path)
            
    def test_update_plugins_by_project_file(self):
        # Create a mock project file
        test_project_data = {
            "Plugins": [
                {"Name": "Plugin1", "Enabled": "true"},
                {"Name": "Plugin2", "Enabled": "false"}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.uproject') as tf:
            json.dump(test_project_data, tf)
            temp_path = tf.name
            
        try:
            # Create a plugins dictionary to update
            plugins = {
                "Plugin1": {"Enabled": False, "InProjectFile": False},
                "Plugin2": {"Enabled": True, "InProjectFile": False},
                "Plugin3": {"Enabled": True, "InProjectFile": False}
            }
            
            # Update plugins
            updated_plugins = update_plugins_by_project_file(temp_path, plugins)
            
            # Check results
            self.assertTrue(updated_plugins["Plugin1"]["Enabled"])
            self.assertTrue(updated_plugins["Plugin1"]["InProjectFile"])
            
            self.assertFalse(updated_plugins["Plugin2"]["Enabled"])
            self.assertTrue(updated_plugins["Plugin2"]["InProjectFile"])
            
            self.assertTrue(updated_plugins["Plugin3"]["Enabled"])
            self.assertFalse(updated_plugins["Plugin3"].get("InProjectFile", False))
            
        finally:
            os.unlink(temp_path)
            
    @patch('ue.project.ue.path.project.get_project_target_files')
    @patch('ue.project.ue.path.project.get_project_name_from_path')
    def test_get_build_targets(self, mock_get_name, mock_get_targets):
        # Mock the dependencies
        mock_get_name.return_value = "TestProject"
        mock_get_targets.return_value = ["TestProjectEditor.Target.cs", "TestProject.Target.cs"]
        
        # Test the function
        targets = get_build_targets("/fake/path")
        self.assertEqual(set(targets), {"Editor", "Game"})
        
    @patch('ue.project.get_build_targets')
    def test_has_build_target(self, mock_get_targets):
        # Mock the dependencies
        mock_get_targets.return_value = ["Editor", "Game"]
        
        # Test the function
        self.assertTrue(has_build_target("/fake/path", "Editor"))
        self.assertTrue(has_build_target("/fake/path", "Game"))
        self.assertFalse(has_build_target("/fake/path", "Client"))
        
    def test_get_engine_id(self):
        # Create a temporary project file
        test_project_data = {
            "EngineAssociation": "4.27"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.uproject') as tf:
            json.dump(test_project_data, tf)
            temp_path = tf.name
            
        try:
            # Test reading engine ID
            engine_id = get_engine_id(temp_path)
            self.assertEqual(engine_id, "4.27")
            
            # Test with UUID format
            with open(temp_path, 'w') as f:
                json.dump({"EngineAssociation": "{1234ABCD-5678-90EF-GHIJ-KLMNOPQRSTUV}"}, f)
            
            engine_id = get_engine_id(temp_path)
            self.assertEqual(engine_id, "1234ABCD-5678-90EF-GHIJ-KLMNOPQRSTUV")
            
        finally:
            os.unlink(temp_path)
            
    @patch('ue.project.get_engine_id')
    @patch('ue.project.ue.path.engine.get_root_path_from_identifier')
    def test_get_engine_root_path(self, mock_get_root, mock_get_id):
        # Mock the dependencies
        mock_get_id.return_value = "4.27"
        mock_get_root.return_value = "/fake/engine/path"
        
        # Test the function
        engine_path = get_engine_root_path("fake.uproject")
        self.assertEqual(engine_path, "/fake/engine/path")
        
        # Test with no engine ID
        mock_get_id.return_value = None
        engine_path = get_engine_root_path("fake.uproject")
        self.assertIsNone(engine_path) 