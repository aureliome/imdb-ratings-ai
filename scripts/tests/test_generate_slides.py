import unittest
import os
import json
import shutil
from scripts.generate_slides import generate_slides

class TestGenerateSlides(unittest.TestCase):
    def setUp(self):
        self.test_dir = 'test_slides_gen'
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
            
        self.stats_file = os.path.join(self.test_dir, 'stats.json')
        self.template_dir = self.test_dir
        self.template_file = 'template.html'
        self.output_file = os.path.join(self.test_dir, 'index.html')
        
        # Create dummy stats
        self.stats_data = {
            "total_days_watched": 10.5,
            "avg_runtime_minutes": 100.2,
            "most_watched_genres": [{"name": "Genre1", "count": 10}, {"name": "Genre2", "count": 5}],
            "favorites": {
                "genres": [{"name": "FavGenre1", "approval_rate": 90.0}],
                "directors": [{"name": "Director1"}],
                "actors": [{"name": "Actor1"}]
            },
            "least_favorites": {
                "genres": [{"name": "BadGenre1", "approval_rate": 10.0}]
            }
        }
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats_data, f)
            
        # Create dummy template
        with open(os.path.join(self.template_dir, self.template_file), 'w') as f:
            f.write("Stats: {{ total_days_watched|int }}, {{ avg_runtime_minutes|int }}")
            f.write("\nMost Watched: {% for g in most_watched_genres %}{{ g.name }} {% endfor %}")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_generate_slides(self):
        generate_slides(self.stats_file, self.template_dir, self.template_file, self.output_file)
        
        self.assertTrue(os.path.exists(self.output_file))
        
        with open(self.output_file, 'r') as f:
            content = f.read()
            
        self.assertIn("Stats: 10, 100", content)
        self.assertIn("Most Watched: Genre1 Genre2", content)

if __name__ == '__main__':
    unittest.main()
