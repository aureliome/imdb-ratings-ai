import json
import os
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

def load_stats(stats_path):
    with open(stats_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_slides(stats_path, template_dir, template_file, output_path, generate_pdf=True):
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
        'favorite_actors': favorite_actors,
        'total_movies': stats.get('total_movies', 0),
        'global_avg_rating': stats.get('global_avg_rating', 0),
        'global_avg_rating': stats.get('global_avg_rating', 0),
        'decades_data': stats.get('decades_data', []),
        'votes_data': stats.get('votes_data', [])
    }
    
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)
    rendered_html = template.render(context)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered_html)
        
    # Generate PDF
    if generate_pdf:
        pdf_path = output_path.replace('.html', '.pdf')
        print(f"Generating PDF at {pdf_path}...")
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            # 1920x1080 to match our print styles
            page = browser.new_page(viewport={'width': 1920, 'height': 1080})
            
            # Convert path to file URL
            file_url = f"file://{output_path}"
            page.goto(file_url, wait_until="networkidle")
            
            # Wait for Chart.js animations to complete
            page.wait_for_timeout(2000)
            
            page.pdf(path=pdf_path, width="1920px", height="1080px", print_background=True)
            browser.close()
    else:
        print("Skipping PDF generation as requested.")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    stats_file = os.path.join(base_dir, 'stats.json')
    slides_dir = os.path.join(base_dir, 'slides')
    template_name = 'template.html'
    output_file = os.path.join(slides_dir, 'index.html')
    
    # Check for SKIP_PDF env var
    skip_pdf = os.environ.get('SKIP_PDF', '').lower() == 'true'
    
    generate_slides(stats_file, slides_dir, template_name, output_file, generate_pdf=not skip_pdf)
    print(f"Slides generated at {output_file}")
