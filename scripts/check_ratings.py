import csv
import sys
from pathlib import Path

RATINGS_FILE = Path(__file__).parent.parent / 'data' / 'ratings-plus.csv'


REQUIRED_COLUMNS = [
    'Const', 'Your Rating', 'Title', 'URL', 'Title Type', 
    'IMDb Rating', 'Runtime (mins)', 'Year', 'Genres', 'Directors', 'Main Actors', 'Countries'
]

def validate_ratings():
    if not RATINGS_FILE.exists():
        print(f"Error: {RATINGS_FILE} does not exist.")
        sys.exit(1)

    try:
        with open(RATINGS_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Check columns
            if not reader.fieldnames:
                print("Error: CSV is empty or has no header.")
                sys.exit(1)
                
            missing_cols = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
            if missing_cols:
                print(f"Error: Missing columns: {missing_cols}")
                sys.exit(1)
            
            row_count = 0
            error_count = 0
            
            for row in reader:
                row_count += 1
                
                # We only care about validation, not filtering here, but we can check types
                # 'Your Rating' should be int 1-10 if present
                rating = row.get('Your Rating')
                if rating:
                    try:
                        r = int(rating)
                        if not (1 <= r <= 10):
                            print(f"Warning: Row {row_count} has invalid rating: {rating}")
                            error_count += 1
                    except ValueError:
                        print(f"Warning: Row {row_count} has non-integer rating: {rating}")
                        error_count += 1

                # 'Year' should be a year
                year = row.get('Year')
                if year:
                    try:
                        int(year)
                    except ValueError:
                        print(f"Warning: Row {row_count} has invalid year: {year}")
                        error_count += 1
                        
    except Exception as e:
        print(f"Error processing CSV: {e}")
        sys.exit(1)

    if error_count > 0:
        print(f"Validation completed with {error_count} warnings.")
        # Decide if we want to fail on warnings. For now, let's pass but report.
        # If strict validation is needed, sys.exit(1)
    else:
        print("Validation successful. ratings.csv is valid.")

if __name__ == "__main__":
    validate_ratings()
