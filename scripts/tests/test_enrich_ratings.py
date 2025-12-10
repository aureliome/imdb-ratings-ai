import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import enrich_ratings

class TestEnrichRatings(unittest.TestCase):

    def test_get_countries_found(self):
        html_content = """
        <html>
            <li>
                <span class="ipc-metadata-list-item__label">Country of origin</span>
                <a class="ipc-metadata-list-item__list-content-item">USA</a>
                <a class="ipc-metadata-list-item__list-content-item">UK</a>
            </li>
        </html>
        """
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        countries = enrich_ratings.get_countries(soup)
        self.assertEqual(countries, "USA, UK")

    def test_get_main_actors_found(self):
        html_content = """
        <html>
            <li>
                <span>Stars</span>
                <a class="ipc-metadata-list-item__list-content-item">Actor One</a>
                <a class="ipc-metadata-list-item__list-content-item">Actor Two</a>
            </li>
        </html>
        """
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        actors = enrich_ratings.get_main_actors(soup)
        self.assertEqual(actors, "Actor One, Actor Two")

    def test_get_metadata_found(self):
        # Mock HTML with "Stars" and "Country of origin"
        html_content = """
        <html>
            <li>
                <span>Stars</span>
                <a class="ipc-metadata-list-item__list-content-item">Actor One</a>
                <a class="ipc-metadata-list-item__list-content-item">Actor Two</a>
            </li>
            <li>
                <span>Country of origin</span>
                <a class="ipc-metadata-list-item__list-content-item">USA</a>
            </li>
        </html>
        """
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = html_content.encode('utf-8')
            mock_get.return_value = mock_response
            
            metadata = enrich_ratings.get_metadata("http://fake.url")
            self.assertEqual(metadata["Main Actors"], "Actor One, Actor Two")
            self.assertEqual(metadata["Countries"], "USA")

    def test_get_metadata_not_found(self):
        html_content = "<html><body>No metadata here</body></html>"
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = html_content.encode('utf-8')
            mock_get.return_value = mock_response
            
            metadata = enrich_ratings.get_metadata("http://fake.url")
            self.assertEqual(metadata["Main Actors"], "")
            self.assertEqual(metadata["Countries"], "")

    def test_get_metadata_error(self):
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            metadata = enrich_ratings.get_metadata("http://fake.url")
            self.assertIsNone(metadata)

    @patch('enrich_ratings.RATINGS_FILE', '/tmp/fake_ratings.csv')
    @patch('enrich_ratings.TEMP_FILE', '/tmp/fake_ratings.csv.tmp')
    @patch('os.path.exists')
    @patch('shutil.copy')
    @patch('shutil.move')
    @patch('time.sleep') # Don't wait in tests
    def test_main_flow(self, mock_sleep, mock_move, mock_copy, mock_exists):
        mock_exists.return_value = True
        
        # Initial CSV content
        # Header without "Main Actors" or "Countries", and one row
        initial_csv = "URL,Title\nhttp://url1,Movie1"
        
        m = mock_open(read_data=initial_csv)
        
        with patch('builtins.open', m):
            with patch('enrich_ratings.get_metadata') as mock_get_metadata:
                mock_get_metadata.return_value = {"Main Actors": "Actor X", "Countries": "Country Y"}
                
                enrich_ratings.main()
                
                # Verify that get_metadata was called for the URL
                mock_get_metadata.assert_called_with("http://url1")
                
                # Check if file was written.
                handle = m()
                self.assertTrue(handle.write.called)
                
                # Check that shutil.move was called
                mock_move.assert_called_with('/tmp/fake_ratings.csv.tmp', '/tmp/fake_ratings.csv')

    @patch('enrich_ratings.RATINGS_FILE', '/tmp/fake_ratings.csv')
    @patch('enrich_ratings.SOURCE_FILE', '/tmp/fake_source.csv')
    @patch('os.path.exists')
    def test_main_file_not_found(self, mock_exists):
        # exists returns False for both RATINGS_FILE and SOURCE_FILE
        # Since os.path.exists is called for RATINGS_FILE then SOURCE_FILE
        mock_exists.side_effect = [False, False]
        
        with patch('builtins.print') as mock_print:
            enrich_ratings.main()
            mock_print.assert_called_with("File not found: /tmp/fake_ratings.csv and source /tmp/fake_source.csv is missing too.")

    @patch('enrich_ratings.RATINGS_FILE', '/tmp/fake_ratings.csv')
    @patch('enrich_ratings.SOURCE_FILE', '/tmp/fake_source.csv')
    @patch('enrich_ratings.TEMP_FILE', '/tmp/fake_ratings.csv.tmp')
    @patch('os.path.exists')
    @patch('shutil.copy')
    @patch('shutil.move')
    @patch('time.sleep')
    def test_main_copy_from_source(self, mock_sleep, mock_move, mock_copy, mock_exists):
        # RATINGS_FILE missing, SOURCE_FILE exists. 
        # Then next check is update loop which opens RATINGS_FILE (which needs to exist now).
        # We need to be careful about mocking here because after copy, the file 'exists' conceptually, 
        # but os.path.exists mock will keep returning what we set.
        # However, the code:
        # if not exists(RATINGS):
        #    if exists(SOURCE): copy
        # with open(RATINGS): ...
        
        # mocking open is handled by mock_open in other tests, but here we might need it.
        # Let's verify the copy call happens.
        
        mock_exists.side_effect = [False, True] 
        
        # We need to mock open to avoid FileNotFoundError when "with open(RATINGS_FILE...)" runs
        initial_csv = "URL,Title\nhttp://url1,Movie1"
        m = mock_open(read_data=initial_csv)
        
        with patch('builtins.open', m):
             with patch('enrich_ratings.get_metadata') as mock_get_metadata:
                mock_get_metadata.return_value = {"Main Actors": "Actor", "Countries": "Country"}
                enrich_ratings.main()
                
                # Check that copy was called
                mock_copy.assert_any_call('/tmp/fake_source.csv', '/tmp/fake_ratings.csv')

if __name__ == '__main__':
    unittest.main()
