import unittest
import os
import tempfile
import shutil
import sys
from unittest.mock import patch, MagicMock
from build import ProjectBuilder, BuildError, get_real_arg_values_list
from build_config import BuildConfig
from argparse import Namespace
import logging

class TestGetRealArgValuesList(unittest.TestCase):
    def test_string_arg(self):
        result = get_real_arg_values_list("Test", ["All", "Values"], "test")
        self.assertEqual(result, ["Test"])
        
    def test_list_arg(self):
        result = get_real_arg_values_list(["Test1", "Test2"], ["All", "Values"], "test")
        self.assertEqual(result, ["Test1", "Test2"])
        
    def test_all_value(self):
        result = get_real_arg_values_list("all", ["All", "Values"], "test")
        self.assertEqual(result, ["All", "Values"])
        
        # Case insensitive
        result = get_real_arg_values_list("ALL", ["All", "Values"], "test")
        self.assertEqual(result, ["All", "Values"])
        
    def test_invalid_arg(self):
        with self.assertRaises(BuildError):
            get_real_arg_values_list(123, ["All", "Values"], "test")

class TestProjectBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary project structure
        cls.test_dir = tempfile.mkdtemp()
        cls.project_name = "TestProject"
        
        # Create project directory structure
        cls.project_dir = os.path.join(cls.test_dir, cls.project_name)
        os.makedirs(cls.project_dir)
        
        # Create dummy .uproject file
        cls.uproject_path = os.path.join(cls.project_dir, f"{cls.project_name}.uproject")
        with open(cls.uproject_path, 'w') as f:
            f.write('{"EngineAssociation": "4.27"}')
            
        # Create some temporary directories to clean
        cls.dirs_to_clean = ['Binaries', 'Intermediate', 'Saved']
        for dir_name in cls.dirs_to_clean:
            os.makedirs(os.path.join(cls.project_dir, dir_name))
            
        # Create Source directory with target files
        cls.source_dir = os.path.join(cls.project_dir, "Source")
        os.makedirs(cls.source_dir)
        
        # Create target files
        with open(os.path.join(cls.source_dir, f"{cls.project_name}.Target.cs"), 'w') as f:
            f.write('// Game target')
        with open(os.path.join(cls.source_dir, f"{cls.project_name}Editor.Target.cs"), 'w') as f:
            f.write('// Editor target')

    @classmethod
    def tearDownClass(cls):
        # Clean up temporary directory
        shutil.rmtree(cls.test_dir)

    def setUp(self):
        # Suppress logging during tests
        logging.disable(logging.CRITICAL)
        
    def tearDown(self):
        # Re-enable logging
        logging.disable(logging.NOTSET)

    def test_project_builder_initialization(self):
        builder = ProjectBuilder()
        self.assertIsNone(builder.config)

    @patch('argparse.ArgumentParser.parse_args')
    @patch('common.process_parsed_args')
    def test_process_args(self, mock_process_args, mock_parse_args):
        # Mock the argument parsing
        mock_args = Namespace(
            source=self.project_dir,
            shellsource=None,
            target="Editor",
            config="Development",
            platform="Win64",
            definitions=None,
            nonUnity=False,
            noPrecompiledHeaders=False,
            onlyDebug=False
        )
        mock_parse_args.return_value = mock_args
        mock_process_args.return_value = False
        
        builder = ProjectBuilder()
        config = builder.process_args()
        
        self.assertIsNotNone(config)
        self.assertEqual(config.source_path, self.project_dir)
        self.assertEqual(config.target, "Editor")
        self.assertEqual(config.config, "Development")
        self.assertEqual(config.platform, "Win64")
        
    @patch('ue.path.project.get_root_path_from_path')
    @patch('ue.path.get_project_file_path')
    @patch('ue.project.get_engine_root_path')
    @patch('ue.path.get_relative_build_file_path')
    def test_init_success(self, mock_build_path, mock_engine_path, mock_project_path, mock_root_path):
        # Mock the dependencies
        mock_root_path.return_value = self.project_dir
        mock_project_path.return_value = self.uproject_path
        mock_engine_path.return_value = "/fake/engine/path"
        mock_build_path.return_value = "Engine/Build/BatchFiles/Build.bat"
        
        # Create a temporary build file
        build_file_dir = os.path.join("/fake/engine/path", "Engine/Build/BatchFiles")
        os.makedirs(build_file_dir, exist_ok=True)
        build_file_path = os.path.join(build_file_dir, "Build.bat")
        with open(build_file_path, 'w') as f:
            f.write('echo "Build script"')
        
        try:
            builder = ProjectBuilder()
            result = builder.init(self.project_dir)
            
            # Since we can't actually create the file at the mocked path, this will fail
            # But we can test the logic up to the file check
            self.assertIsNone(result)
            
            # Test with patch to bypass file existence check
            with patch('os.path.isfile', return_value=True):
                result = builder.init(self.project_dir)
                self.assertEqual(result[0], os.path.normpath("/fake/engine/path/Engine/Build/BatchFiles/Build.bat"))
                self.assertEqual(result[1], self.uproject_path)
        
        finally:
            if os.path.exists(build_file_dir):
                shutil.rmtree(os.path.dirname(build_file_dir))
                
    def test_init_failure(self):
        # Test with invalid source path
        builder = ProjectBuilder()
        result = builder.init("/nonexistent/path")
        self.assertIsNone(result)
        
    @patch('build.ProjectBuilder.init')
    @patch('build.ProjectBuilder.run_build')
    @patch('build.ProjectBuilder.process_args')
    def test_run(self, mock_process_args, mock_run_build, mock_init):
        # Mock the dependencies
        mock_config = BuildConfig(source_path=self.project_dir)
        mock_process_args.return_value = mock_config
        mock_init.return_value = ("/fake/build.bat", self.uproject_path)
        
        # Test successful run
        builder = ProjectBuilder()
        builder.run()
        
        mock_init.assert_called_once_with(self.project_dir)
        mock_run_build.assert_called_once_with("/fake/build.bat", self.uproject_path)
        
        # Test when init returns None
        mock_init.reset_mock()
        mock_run_build.reset_mock()
        mock_init.return_value = None
        
        builder = ProjectBuilder()
        builder.run()
        
        mock_init.assert_called_once_with(self.project_dir)
        mock_run_build.assert_not_called()
        
    @patch('build.get_real_arg_values_list')
    @patch('ue.path.get_project_name_from_project_file_path')
    @patch('ue.project.get_build_targets')
    def test_run_build(self, mock_get_targets, mock_get_name, mock_get_values):
        # Mock the dependencies
        mock_get_name.return_value = "TestProject"
        mock_get_targets.return_value = ["Editor", "Game"]
        mock_get_values.side_effect = lambda arg, all_val, desc: ["Editor"] if desc == "target" else ["Development"] if desc == "configuration" else ["Win64"]
        
        # Mock run_single_build
        with patch('build.ProjectBuilder.run_single_build') as mock_run_single:
            builder = ProjectBuilder()
            builder.config = BuildConfig(
                source_path=self.project_dir,
                target="Editor",
                config="Development",
                platform="Win64"
            )
            
            builder.run_build("/fake/build.bat", self.uproject_path)
            
            mock_run_single.assert_called_once_with(
                "/fake/build.bat", 
                self.uproject_path, 
                "TestProject", 
                "Development", 
                "Editor", 
                "Win64"
            )
            
    @patch('build.ProjectBuilder.get_target_arg')
    @patch('subprocess.Popen')
    def test_run_single_build(self, mock_popen, mock_get_target):
        # Mock the dependencies
        mock_get_target.return_value = "TestProjectEditor"
        
        # Mock successful process
        process_mock = MagicMock()
        process_mock.returncode = 0
        process_mock.communicate.return_value = (b"Build succeeded", b"")
        mock_popen.return_value = process_mock
        
        builder = ProjectBuilder()
        builder.config = BuildConfig(
            source_path=self.project_dir,
            target="Editor",
            config="Development",
            platform="Win64",
            definitions=["TEST=1"],
            non_unity=True,
            no_precompiled_headers=True,
            debug_only=False
        )
        
        # Test successful build
        builder.run_single_build(
            "/fake/build.bat", 
            self.uproject_path, 
            "TestProject", 
            "Development", 
            "Editor", 
            "Win64"
        )
        
        # Check command construction
        expected_cmd = [
            "/fake/build.bat", 
            "TestProjectEditor", 
            "Win64", 
            "Development", 
            self.uproject_path,
            "-define:TEST=1",
            "-DisableUnity",
            "-NoSharedPCH",
            "-NoPCH"
        ]
        
        mock_popen.assert_called_once()
        actual_cmd = mock_popen.call_args[0][0]
        self.assertEqual(actual_cmd, expected_cmd)
        
        # Test failed build
        mock_popen.reset_mock()
        process_mock.returncode = 1
        process_mock.communicate.return_value = (b"", b"Build failed")
        
        with self.assertRaises(BuildError):
            builder.run_single_build(
                "/fake/build.bat", 
                self.uproject_path, 
                "TestProject", 
                "Development", 
                "Editor", 
                "Win64"
            )
            
        # Test debug only mode
        mock_popen.reset_mock()
        builder.config.debug_only = True
        
        builder.run_single_build(
            "/fake/build.bat", 
            self.uproject_path, 
            "TestProject", 
            "Development", 
            "Editor", 
            "Win64"
        )
        
        mock_popen.assert_not_called() 