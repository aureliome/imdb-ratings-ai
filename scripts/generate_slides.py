import json
import os
from jinja2 import Environment, FileSystemLoader

def load_stats(stats_path):
    with open(stats_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_slides(stats_path, template_dir, template_file, output_path):
    stats = load_stats(stats_path)
    
    # Prepare data for template
    total_days_watched = stats.get('total_days_watched', 0)
    avg_runtime_minutes = stats.get('avg_runtime_minutes', 0)
    
    # Most Watched
    most_watched_genres = stats.get('most_watched_genres', [])[:5]
    
    # Favorites
    favorites = stats.get('favorites', {})
    favorite_genres = favorites.get('genres', [])
    # Sort by approval rate desc just in case, though JSON seems sorted?
    # Actually based on viewing, JSON had Western (80), Guerra (76), Musical (58), Noir (50).
    # It seems sorted. We take top 5.
    favorite_genres = sorted(favorite_genres, key=lambda x: x['approval_rate'], reverse=True)[:5]
    
    favorite_directors = favorites.get('directors', [])
    favorite_actors = favorites.get('actors', [])
    
    # Least Favorites
    least_favorites = stats.get('least_favorites', {})
    least_favorite_genres_list = least_favorites.get('genres', [])
    # Sort by approval rate asc
    least_favorite_genres = sorted(least_favorite_genres_list, key=lambda x: x['approval_rate'])[:5]
    
    context = {
        'total_days_watched': total_days_watched,
        'avg_runtime_minutes': avg_runtime_minutes,
        'most_watched_genres': most_watched_genres,
        'favorite_genres': favorite_genres,
        'least_favorite_genres': least_favorite_genres,
        'favorite_directors': favorite_directors,
        'favorite_actors': favorite_actors
    }
    
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)
    rendered_html = template.render(context)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered_html)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    stats_file = os.path.join(base_dir, 'stats.json')
    slides_dir = os.path.join(base_dir, 'slides')
    template_name = 'template.html'
    output_file = os.path.join(slides_dir, 'index.html')
    
    generate_slides(stats_file, slides_dir, template_name, output_file)
    print(f"Slides generated at {output_file}")
