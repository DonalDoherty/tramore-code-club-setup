#!/usr/bin/env python3
"""
Basic unit tests for tramore_code_club.py
Tests the core refactored functionality
"""

import unittest
import tempfile
import shutil
import os
from pathlib import Path
import sys

# Import the module to test
import tramore_code_club as tcc


class TestTramoreCodeClub(unittest.TestCase):
    """Test cases for Tramore Code Club functions"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        # Remove the temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_get_safe_name(self):
        """Test safe name generation from student names"""
        self.assertEqual(tcc.get_safe_name("John Doe"), "john-doe")
        self.assertEqual(tcc.get_safe_name("Mary Smith"), "mary-smith")
        self.assertEqual(tcc.get_safe_name("Bob"), "bob")
        self.assertEqual(tcc.get_safe_name("Alice O'Brien"), "alice-o'brien")
        self.assertEqual(tcc.get_safe_name(""), "unknown")
        self.assertEqual(tcc.get_safe_name("   "), "unknown")

    def test_count_files_by_type(self):
        """Test file counting functionality"""
        # Create test files
        test_folder = os.path.join(self.test_dir, "test_student")
        os.makedirs(test_folder)

        # Create some test files
        Path(os.path.join(test_folder, "program.py")).touch()
        Path(os.path.join(test_folder, "test.py")).touch()
        Path(os.path.join(test_folder, "notes.txt")).touch()
        Path(os.path.join(test_folder, "readme.md")).touch()

        # Create a subdirectory with files
        subdir = os.path.join(test_folder, "subdir")
        os.makedirs(subdir)
        Path(os.path.join(subdir, "another.py")).touch()

        counts = tcc.count_files_by_type(test_folder)

        self.assertEqual(counts["python"], 3)  # 3 .py files
        self.assertEqual(counts["text"], 1)    # 1 .txt file
        self.assertEqual(counts["other"], 1)   # 1 .md file
        self.assertEqual(counts["total"], 5)   # 5 files total
        self.assertEqual(counts["dirs"], 1)    # 1 subdirectory

    def test_copy_all_files(self):
        """Test recursive file copying"""
        # Create source directory with files
        src_dir = os.path.join(self.test_dir, "source")
        os.makedirs(src_dir)

        # Create test files
        with open(os.path.join(src_dir, "file1.txt"), "w", encoding="utf-8") as f:
            f.write("Test content 1")

        subdir = os.path.join(src_dir, "subdir")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "file2.txt"), "w", encoding="utf-8") as f:
            f.write("Test content 2")

        # Create destination directory
        dest_dir = os.path.join(self.test_dir, "dest")

        # Copy files
        file_count = tcc.copy_all_files(src_dir, dest_dir)

        # Verify copy
        self.assertEqual(file_count, 2)
        self.assertTrue(os.path.exists(os.path.join(dest_dir, "file1.txt")))
        self.assertTrue(os.path.exists(os.path.join(dest_dir, "subdir", "file2.txt")))

        # Verify content
        with open(os.path.join(dest_dir, "file1.txt"), "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "Test content 1")

    def test_copy_all_files_excludes_dirs(self):
        """Test that excluded directories are not copied"""
        # Create source directory with .git folder
        src_dir = os.path.join(self.test_dir, "source")
        os.makedirs(src_dir)

        # Create a .git directory (should be excluded)
        git_dir = os.path.join(src_dir, ".git")
        os.makedirs(git_dir)
        with open(os.path.join(git_dir, "config"), "w", encoding="utf-8") as f:
            f.write("git config")

        # Create a normal file
        with open(os.path.join(src_dir, "file.txt"), "w", encoding="utf-8") as f:
            f.write("normal file")

        # Copy files
        dest_dir = os.path.join(self.test_dir, "dest")
        file_count = tcc.copy_all_files(src_dir, dest_dir)

        # Verify .git directory was not copied
        self.assertFalse(os.path.exists(os.path.join(dest_dir, ".git")))
        self.assertTrue(os.path.exists(os.path.join(dest_dir, "file.txt")))
        self.assertEqual(file_count, 1)

    def test_configure_git_identity(self):
        """Test Git identity configuration (basic check)"""
        # This is a basic test that the function exists and has proper signature
        # Full testing would require a git repository
        self.assertTrue(callable(tcc.configure_git_identity))

    def test_setup_logging(self):
        """Test that logging is properly configured"""
        # Verify logger exists
        self.assertIsNotNone(tcc.logger)
        self.assertEqual(tcc.logger.name, "TramoreCodeClub")

        # Verify logger has handlers
        self.assertGreater(len(tcc.logger.handlers), 0)


class TestConstants(unittest.TestCase):
    """Test that constants are properly defined"""

    def test_constants_exist(self):
        """Test that all expected constants are defined"""
        self.assertTrue(hasattr(tcc, 'REPO_NAME'))
        self.assertTrue(hasattr(tcc, 'MAIN_BRANCH'))
        self.assertTrue(hasattr(tcc, 'STUDENT_BRANCH_PREFIX'))
        self.assertTrue(hasattr(tcc, 'STUDENTS_SUBDIR'))
        self.assertTrue(hasattr(tcc, 'DEFAULT_GIT_NAME'))
        self.assertTrue(hasattr(tcc, 'DEFAULT_GIT_EMAIL'))
        self.assertTrue(hasattr(tcc, 'EXCLUDE_DIRS'))

    def test_constant_values(self):
        """Test that constants have expected values"""
        self.assertEqual(tcc.MAIN_BRANCH, "main")
        self.assertEqual(tcc.STUDENT_BRANCH_PREFIX, "student/")
        self.assertEqual(tcc.STUDENTS_SUBDIR, "students")
        self.assertEqual(tcc.EXCLUDE_DIRS, ['.git'])


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
