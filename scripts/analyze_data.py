
import csv
import json
import statistics
import os

def load_data(filepath):
    movies = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Title Type'] == 'Film':
                # Convert numeric fields
                try:
                    row['Your Rating'] = float(row['Your Rating'])
                    row['Runtime (mins)'] = int(row['Runtime (mins)'])
                except ValueError:
                    continue # Skip bad data
                movies.append(row)
    return movies

def process_category(movies, key_extractor, min_count=3):
    """
    key_extractor: function that takes a movie row and returns a list of keys (e.g. genres)
    """
    stats = {}
    
    for movie in movies:
        keys = key_extractor(movie)
        rating = movie['Your Rating']
        liked = 1 if rating >= 7 else 0
        
        for k in keys:
            if k not in stats:
                stats[k] = {'count': 0, 'sum_rating': 0, 'liked_count': 0, 'movies': []}
            stats[k]['count'] += 1
            stats[k]['sum_rating'] += rating
            stats[k]['liked_count'] += liked
            stats[k]['movies'].append(movie['Original Title'])
            
    # Calculate derived metrics
    results = []
    for k, v in stats.items():
        if v['count'] < min_count:
            continue
            
        approval_rate = (v['liked_count'] / v['count']) * 100
        avg_rating = v['sum_rating'] / v['count']
        
        results.append({
            'name': k,
            'count': v['count'],
            'approval_rate': approval_rate,
            'avg_rating': avg_rating,
            'movies': v['movies'] # useful for debugging or detailed lists
        })
        
    return results

def get_genres(movie):
    genres = movie['Genres'].split(', ')
    # Merge "Musica" and "Musical"
    genres = ['Musical' if g == 'Musica' else g for g in genres]
    return [g.strip() for g in genres if g.strip()]

def get_directors(movie):
    directors = movie['Directors'].split(',')
    return [d.strip() for d in directors if d.strip()]

def get_actors(movie):
    # Main Actors column, assume comma separated
    if not movie.get('Main Actors'):
        return []
    actors = movie['Main Actors'].split(',')
    return [a.strip() for a in actors if a.strip()]

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_file = os.path.join(base_dir, 'data', 'ratings-plus.csv')
    movies = load_data(data_file)
    
    # 1. Total Runtime
    total_minutes = sum(m['Runtime (mins)'] for m in movies)
    total_days = total_minutes / (60 * 24)
    
    # 2. Avg Runtime (All Movies)
    if movies:
        avg_runtime_minutes = statistics.mean([m['Runtime (mins)'] for m in movies])
    else:
        avg_runtime_minutes = 0
        
    # 3. Analyze Categories
    genres_stats = process_category(movies, get_genres, min_count=3)
    directors_stats = process_category(movies, get_directors, min_count=2) # Directors might be fewer per movie
    actors_stats = process_category(movies, get_actors, min_count=3)
    
    # Sort helper
    def sort_key(x):
        return (x['approval_rate'], x['avg_rating'])
        
    genres_sorted = sorted(genres_stats, key=sort_key, reverse=True)
    directors_sorted = sorted(directors_stats, key=sort_key, reverse=True)
    actors_sorted = sorted(actors_stats, key=sort_key, reverse=True)
    
    # Most watched genres
    most_watched_genres = sorted(genres_stats, key=lambda x: x['count'], reverse=True)

    output = {
        'total_days_watched': total_days,
        'avg_runtime_minutes': avg_runtime_minutes,
        'favorites': {
            'genres': genres_sorted[:5],
            'directors': directors_sorted[:5],
            'actors': actors_sorted[:5]
        },
        'least_favorites': {
            'genres': genres_sorted[-5:]
        },
        'most_watched_genres': most_watched_genres[:5]
    }
    
    with open('stats.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

if __name__ == '__main__':
    main()
