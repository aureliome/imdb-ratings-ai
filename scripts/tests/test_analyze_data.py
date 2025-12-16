
import unittest
from scripts import analyze_data

class TestAnalyzeData(unittest.TestCase):
    def test_get_genres_merge(self):
        movie = {'Genres': 'Musica, Drammatico'}
        genres = analyze_data.get_genres(movie)
        self.assertIn('Musical', genres)
        self.assertIn('Drammatico', genres)
        self.assertNotIn('Musica', genres)

    def test_process_category(self):
        movies = [
            {'Title': 'A', 'Original Title': 'A', 'Your Rating': 8.0},
            {'Title': 'B', 'Original Title': 'B', 'Your Rating': 6.0},
            {'Title': 'C', 'Original Title': 'C', 'Your Rating': 9.0}
        ]
        # Dummy extractor maps all to 'TestGenre'
        def extractor(m): return ['TestGenre']
        
        results = analyze_data.process_category(movies, extractor, min_count=1)
        self.assertEqual(len(results), 1)
        stat = results[0]
        self.assertEqual(stat['name'], 'TestGenre')
        self.assertEqual(stat['count'], 3)
        self.assertAlmostEqual(stat['avg_rating'], 23.0/3)
        # Liked: A(8), C(9) -> 2 liked
        self.assertAlmostEqual(stat['approval_rate'], (2/3)*100)

if __name__ == '__main__':
    unittest.main()
