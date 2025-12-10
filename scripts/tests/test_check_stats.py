import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import json
from pathlib import Path

# Add scripts directory to sys.path so we can import the module
# This assumes the test file is checking ../../check_stats.py relative to its own location
sys.path.append(str(Path(__file__).parent.parent))

# Import the module to be tested
import check_stats

class TestCheckStats(unittest.TestCase):
    
    @patch('check_stats.STATS_FILE')
    def test_file_not_exists(self, mock_file):
        """Test validation fails when stats.json does not exist."""
        mock_file.exists.return_value = False
        
        with patch('sys.stdout', new=MagicMock()) as mock_stdout:
            with self.assertRaises(SystemExit) as cm:
                check_stats.validate_stats()
            
            self.assertEqual(cm.exception.code, 1)

    @patch('check_stats.STATS_FILE')
    def test_invalid_json_format(self, mock_file):
        """Test validation fails when file contains invalid JSON."""
        mock_file.exists.return_value = True
        
        with patch('builtins.open', mock_open(read_data="{ invalid json")):
            with patch('sys.stdout', new=MagicMock()):
                with self.assertRaises(SystemExit) as cm:
                    check_stats.validate_stats()
                self.assertEqual(cm.exception.code, 1)

    @patch('check_stats.STATS_FILE')
    def test_missing_root_key(self, mock_file):
        """Test validation fails when a required root key is missing."""
        mock_file.exists.return_value = True
        data = {
            "total_days_watched": 10,
            # "avg_runtime_liked_minutes" key is missing
            "favorites": {}, 
            "least_favorites": {}, 
            "most_watched_genres": []
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(data))):
             with patch('sys.stdout', new=MagicMock()):
                with self.assertRaises(SystemExit) as cm:
                    check_stats.validate_stats()
                self.assertEqual(cm.exception.code, 1)

    @patch('check_stats.STATS_FILE')
    def test_invalid_favorites_structure(self, mock_file):
        """Test validation fails when sub-structure (favorites items) is invalid."""
        mock_file.exists.return_value = True
        data = {
            "total_days_watched": 10,
            "avg_runtime_liked_minutes": 100,
            "favorites": {
                "genres": [{"name": "G1"}], # Missing other required keys like count, approval_rate etc.
                "directors": [],
                "actors": [] 
            }, 
            "least_favorites": {"genres": []}, 
            "most_watched_genres": []
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(data))):
             with patch('sys.stdout', new=MagicMock()):
                with self.assertRaises(SystemExit) as cm:
                    check_stats.validate_stats()
                self.assertEqual(cm.exception.code, 1)

    @patch('check_stats.STATS_FILE')
    def test_valid_json(self, mock_file):
        """Test validation passes with a correctly structured JSON."""
        mock_file.exists.return_value = True
        
        valid_item = {
            "name": "Test",
            "count": 5,
            "approval_rate": 80.0,
            "avg_rating": 7.5,
            "movies": ["M1", "M2"]
        }
        
        data = {
            "total_days_watched": 10,
            "avg_runtime_liked_minutes": 100,
            "favorites": {
                "genres": [valid_item],
                "directors": [],
                "actors": [] 
            }, 
            "least_favorites": {"genres": []}, 
            "most_watched_genres": [valid_item]
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(data))):
             with patch('sys.stdout', new=MagicMock()) as mock_stdout:
                check_stats.validate_stats()
                # Should run to completion without SystemExit

if __name__ == '__main__':
    unittest.main()
