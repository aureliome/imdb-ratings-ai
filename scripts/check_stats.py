import json
import sys
from pathlib import Path

# Path validation
STATS_FILE = Path(__file__).parent.parent / 'stats.json'

def validate_item_list(items, context):
    if not isinstance(items, list):
        print(f"Error: '{context}' must be a list.")
        return False
    
    valid = True
    required_keys = ['name', 'count', 'approval_rate', 'avg_rating', 'movies']
    # decades_data has slightly different keys (decade instead of name) so we handle it separately
    
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            print(f"Error: Item {i} in '{context}' is not a dictionary.")
            valid = False
            continue
            
        for key in required_keys:
            if key not in item:
                print(f"Error: Item {i} in '{context}' is missing key '{key}'.")
                valid = False
            # Check for null values if needed
            elif item[key] is None:
                 print(f"Error: Item {i} in '{context}' has null value for key '{key}'.")
                 valid = False

        if 'movies' in item and not isinstance(item['movies'], list):
            print(f"Error: 'movies' in item {i} of '{context}' is not a list.")
            valid = False
            
    return valid

def validate_stats():
    if not STATS_FILE.exists():
        print(f"Error: {STATS_FILE} does not exist.")
        sys.exit(1)
        
    try:
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading stats.json: {e}")
        sys.exit(1)
            
    if not isinstance(data, dict):
        print("Error: Root of stats.json must be a dictionary.")
        sys.exit(1)
        
    required_root_keys = ['total_days_watched', 'avg_runtime_minutes', 'favorites', 'least_favorites', 'most_watched_genres']
    
    valid = True
    for key in required_root_keys:
        if key not in data:
            print(f"Error: Missing root key '{key}'.")
            valid = False
        elif data[key] is None:
            print(f"Error: Root key '{key}' is null.")
            valid = False
            
    if not valid:
        sys.exit(1)

    # Validate favorites
    favorites = data.get('favorites')
    # Since we checked required_root_keys, favorites is present and not None. 
    # But it must be a dict.
    if not isinstance(favorites, dict):
             print(f"Error: 'favorites' must be a dictionary, got {type(favorites).__name__}.")
             valid = False
    else:
        for key in ['genres', 'directors', 'actors']:
            if key not in favorites:
                print(f"Error: 'favorites' is missing key '{key}'.")
                valid = False
            else:
                if not validate_item_list(favorites[key], f"favorites.{key}"):
                    valid = False

    # Validate least_favorites
    least_favorites = data.get('least_favorites')
    if not isinstance(least_favorites, dict):
             print(f"Error: 'least_favorites' must be a dictionary, got {type(least_favorites).__name__}.")
             valid = False
    else:
        if 'genres' not in least_favorites:
             print("Error: 'least_favorites' is missing key 'genres'.")
             valid = False
        else:
             if not validate_item_list(least_favorites['genres'], "least_favorites.genres"):
                  valid = False
                  
    # Validate most_watched_genres
    most_watched = data.get('most_watched_genres')
    if not validate_item_list(most_watched, "most_watched_genres"):
        valid = False

    # Validate decades_data
    decades_data = data.get('decades_data')
    if decades_data is None:
        print("Error: 'decades_data' is missing (was 'years_data').")
        valid = False
    elif not isinstance(decades_data, list):
        print(f"Error: 'decades_data' must be a list, got {type(decades_data).__name__}.")
        valid = False
    else:
        # Custom validation for decades list as it has different keys than 'validate_item_list' expects
        for i, item in enumerate(decades_data):
            if not isinstance(item, dict):
                print(f"Error: Item {i} in 'decades_data' is not a dictionary.")
                valid = False
                continue
            if 'decade' not in item:
                 print(f"Error: Item {i} in 'decades_data' is missing key 'decade'.")
                 valid = False
            if 'count' not in item:
                 print(f"Error: Item {i} in 'decades_data' is missing key 'count'.")
                 valid = False
            if 'avg_rating' not in item:
                 print(f"Error: Item {i} in 'decades_data' is missing key 'avg_rating'.")
                 valid = False
        
    if not valid:
        print("Validation failed with errors.")
        sys.exit(1)
        
    print("Validation successful. stats.json is valid.")

if __name__ == "__main__":
    validate_stats()
