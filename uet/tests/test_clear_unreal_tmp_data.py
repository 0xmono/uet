import unittest
import os
import tempfile
import shutil
import sys
from unittest.mock import patch, MagicMock
import clear_unreal_tmp_data

class TestClearUnrealTmpData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory structure
        cls.test_dir = tempfile.mkdtemp()
        
        # Create test directories to clean
        cls.dirs_to_clean = ['Binaries', 'Intermediate', 'Saved']
        for dir_name in cls.dirs_to_clean:
            # Create at root level
            os.makedirs(os.path.join(cls.test_dir, dir_name))
            
            # Create a file in each directory
            with open(os.path.join(cls.test_dir, dir_name, 'test.txt'), 'w') as f:
                f.write('Test file')
                
            # Create nested directories
            nested_dir = os.path.join(cls.test_dir, 'Project', dir_name)
            os.makedirs(nested_dir)
            with open(os.path.join(nested_dir, 'test.txt'), 'w') as f:
                f.write('Test file in nested directory')
                
        # Create directories that should not be cleaned
        cls.dirs_to_keep = ['Source', 'Content']
        for dir_name in cls.dirs_to_keep:
            os.makedirs(os.path.join(cls.test_dir, dir_name))
            with open(os.path.join(cls.test_dir, dir_name, 'test.txt'), 'w') as f:
                f.write('Test file that should not be deleted')

    @classmethod
    def tearDownClass(cls):
        # Clean up temporary directory
        shutil.rmtree(cls.test_dir)

    @patch('clear_unreal_tmp_data.WORKING_DIRECTORY')
    def test_clear_folders_default(self, mock_working_dir):
        # Set the working directory to our test directory
        mock_working_dir.__str__ = lambda x: self.test_dir
        
        # Run the clear_folders function with default arguments
        with patch('sys.stdout'):  # Suppress print output
            clear_unreal_tmp_data.clear_folders()
            
        # Check that the directories were deleted
        for dir_name in self.dirs_to_clean:
            self.assertFalse(os.path.exists(os.path.join(self.test_dir, dir_name)))
            self.assertFalse(os.path.exists(os.path.join(self.test_dir, 'Project', dir_name)))
            
        # Check that other directories were not deleted
        for dir_name in self.dirs_to_keep:
            self.assertTrue(os.path.exists(os.path.join(self.test_dir, dir_name)))
            
        # Recreate the directories for other tests
        for dir_name in self.dirs_to_clean:
            os.makedirs(os.path.join(self.test_dir, dir_name))
            os.makedirs(os.path.join(self.test_dir, 'Project', dir_name))

    @patch('clear_unreal_tmp_data.WORKING_DIRECTORY')
    def test_clear_folders_custom(self, mock_working_dir):
        # Set the working directory to our test directory
        mock_working_dir.__str__ = lambda x: self.test_dir
        
        # Run the clear_folders function with custom arguments
        with patch('sys.stdout'):  # Suppress print output
            clear_unreal_tmp_data.clear_folders('Binaries')
            
        # Check that only Binaries directories were deleted
        self.assertFalse(os.path.exists(os.path.join(self.test_dir, 'Binaries')))
        self.assertFalse(os.path.exists(os.path.join(self.test_dir, 'Project', 'Binaries')))
        
        # Check that other directories were not deleted
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'Intermediate')))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'Saved')))
        
        # Recreate the directories for other tests
        os.makedirs(os.path.join(self.test_dir, 'Binaries'))
        os.makedirs(os.path.join(self.test_dir, 'Project', 'Binaries'))

    @patch('clear_unreal_tmp_data.WORKING_DIRECTORY')
    def test_clear_folders_invalid_args(self, mock_working_dir):
        # Set the working directory to our test directory
        mock_working_dir.__str__ = lambda x: self.test_dir
        
        # Test with invalid argument type
        with self.assertRaises(TypeError):
            clear_unreal_tmp_data.clear_folders(123)
            
        # Test with mixed valid and invalid arguments
        with self.assertRaises(TypeError):
            clear_unreal_tmp_data.clear_folders('Binaries', 123, 'Saved')

    @patch('sys.argv')
    @patch('clear_unreal_tmp_data.clear_folders')
    def test_main_function(self, mock_clear_folders, mock_argv):
        # Test with valid arguments
        mock_argv.__getitem__.side_effect = lambda idx: ['clear_unreal_tmp_data.py', 'clear_folders', 'Binaries', 'Intermediate'][idx]
        mock_argv.__len__.return_value = 4
        
        clear_unreal_tmp_data.main()
        
        mock_clear_folders.assert_called_once_with('Binaries', 'Intermediate')
        
        # Test with no arguments
        mock_argv.__getitem__.side_effect = lambda idx: ['clear_unreal_tmp_data.py'][idx]
        mock_argv.__len__.return_value = 1
        
        clear_unreal_tmp_data.main()
        
        # Should not call clear_folders again
        mock_clear_folders.assert_called_once()
        
        # Test with invalid function name
        mock_argv.__getitem__.side_effect = lambda idx: ['clear_unreal_tmp_data.py', 'invalid_function'][idx]
        mock_argv.__len__.return_value = 2
        
        clear_unreal_tmp_data.main()
        
        # Should not call clear_folders again
        mock_clear_folders.assert_called_once() 