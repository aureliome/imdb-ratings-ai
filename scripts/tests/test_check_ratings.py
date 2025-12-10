import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os
from pathlib import Path

# Add the scripts directory to sys.path so we can import the module
sys.path.append(str(Path(__file__).parent.parent))

import check_ratings

class TestCheckRatings(unittest.TestCase):
    
    @patch('check_ratings.RATINGS_FILE')
    def test_file_not_exists(self, mock_file):
        mock_file.exists.return_value = False
        
        with patch('sys.stdout', new=MagicMock()) as mock_stdout:
            with self.assertRaises(SystemExit) as cm:
                check_ratings.validate_ratings()
            
            self.assertEqual(cm.exception.code, 1)
            # Verify the error message was printed
            # mock_stdout.write.assert_called() # Hard to check exact string with print being complex

    @patch('check_ratings.RATINGS_FILE')
    def test_csv_empty(self, mock_file):
        mock_file.exists.return_value = True
        
        # Mock opening an empty file (or file with just header effectively empty for DictReader if no rows?)
        # Actually DictReader needs fieldnames.
        
        with patch('builtins.open', mock_open(read_data="")):
            with patch('sys.stdout', new=MagicMock()):
                with self.assertRaises(SystemExit) as cm:
                    check_ratings.validate_ratings()
                self.assertEqual(cm.exception.code, 1)

    @patch('check_ratings.RATINGS_FILE')
    def test_missing_columns(self, mock_file):
        mock_file.exists.return_value = True
        
        # Mock CSV with missing columns
        csv_data = "Const,Your Rating\n1,10"
        
        with patch('builtins.open', mock_open(read_data=csv_data)):
            with patch('sys.stdout', new=MagicMock()):
                with self.assertRaises(SystemExit) as cm:
                    check_ratings.validate_ratings()
                self.assertEqual(cm.exception.code, 1)

    @patch('check_ratings.RATINGS_FILE')
    def test_valid_csv(self, mock_file):
        mock_file.exists.return_value = True
        
        # Valid CSV data
        headers = ",".join(check_ratings.REQUIRED_COLUMNS)
        row1 = "tt1074638,8,Skyfall,http://url,Film,7.8,143,2012,Action,Sam Mendes,Daniel Craig,UK"
        csv_data = f"{headers}\n{row1}"
        
        with patch('builtins.open', mock_open(read_data=csv_data)):
            with patch('sys.stdout', new=MagicMock()) as mock_stdout:
                check_ratings.validate_ratings()
                # Should not raise SystemExit
                # Could check for success message

    @patch('check_ratings.RATINGS_FILE')
    def test_invalid_rating(self, mock_file):
        mock_file.exists.return_value = True
        
        headers = ",".join(check_ratings.REQUIRED_COLUMNS)
        # Rating 11 is invalid
        row1 = "tt1074638,11,Skyfall,http://url,Film,7.8,143,2012,Action,Sam Mendes,Daniel Craig,UK"
        csv_data = f"{headers}\n{row1}"
        
        with patch('builtins.open', mock_open(read_data=csv_data)):
            with patch('sys.stdout', new=MagicMock()) as mock_stdout:
                # The script does not exit on warning, it just prints warning
                check_ratings.validate_ratings()
                
                # Verify warning was printed (optional, but good practice)
                # We can check if any print call contained "Warning"

    @patch('check_ratings.RATINGS_FILE')
    def test_non_integer_rating(self, mock_file):
        mock_file.exists.return_value = True
        
        headers = ",".join(check_ratings.REQUIRED_COLUMNS)
        # Rating 'bad' is invalid
        row1 = "tt1074638,bad,Skyfall,http://url,Film,7.8,143,2012,Action,Sam Mendes,Daniel Craig,UK"
        csv_data = f"{headers}\n{row1}"
        
        with patch('builtins.open', mock_open(read_data=csv_data)):
            with patch('sys.stdout', new=MagicMock()):
                check_ratings.validate_ratings()

    @patch('check_ratings.RATINGS_FILE')
    def test_invalid_year(self, mock_file):
        mock_file.exists.return_value = True
        
        headers = ",".join(check_ratings.REQUIRED_COLUMNS)
        row1 = "tt1074638,8,Skyfall,http://url,Film,7.8,143,bad_year,Action,Sam Mendes,Daniel Craig,UK"
        csv_data = f"{headers}\n{row1}"
        
        with patch('builtins.open', mock_open(read_data=csv_data)):
            with patch('sys.stdout', new=MagicMock()):
                check_ratings.validate_ratings()

if __name__ == '__main__':
    unittest.main()
