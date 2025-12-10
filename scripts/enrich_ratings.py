import csv
import time
import random
import requests
import os
import shutil
from bs4 import BeautifulSoup


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RATINGS_FILE = os.path.join(DATA_DIR, 'ratings-plus.csv')
SOURCE_FILE = os.path.join(DATA_DIR, 'ratings.csv')
TEMP_FILE = RATINGS_FILE + '.tmp'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}


def get_main_actors(soup):
    """
    Extracts 'Stars' from the soup.
    """
    stars = []
    label_span = soup.find('span', string='Stars')
    if not label_span:
         label_span = soup.find('a', string='Stars')
         
    if label_span:
         parent = label_span.find_parent('li')
         if parent:
             links = parent.find_all('a', class_='ipc-metadata-list-item__list-content-item')
             stars = [a.text.strip() for a in links]
    
    if not stars:
         cast_items = soup.select('div[data-testid="title-cast-item"] a[data-testid="title-cast-item__actor"]')
         stars = [a.text.strip() for a in cast_items[:3]]
         
    return ", ".join(stars)


def get_countries(soup):
    """
    Extracts 'Country of origin' from the soup.
    """
    countries = []
    # Search for the label "Country of origin" or "Countries of origin"
    # IMDb usually uses a specific data-testid or label
    
    # Try finding the label span
    label_span = soup.find('span', string='Country of origin')
    if not label_span:
         label_span = soup.find('a', string='Country of origin')
    if not label_span:
         label_span = soup.find('span', string='Countries of origin')

    if label_span:
         # usually in a list item, we want the links following it
         parent = label_span.find_parent('li')
         if parent:
             links = parent.find_all('a', class_='ipc-metadata-list-item__list-content-item')
             countries = [a.text.strip() for a in links]

    if not countries:
         # Fallback: Try looking for a specific testid if known, or loose search
         # For now, let's rely on the label search which is fairly standard on IMDb
         pass
         
    return ", ".join(countries)

def get_metadata(url):
    """
    Fetches the IMDb page and extracts metadata (actors, countries).
    """
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Actors
        actors = get_main_actors(soup)
             
        # Countries
        countries = get_countries(soup)
             
        return {
            "Main Actors": actors,
            "Countries": countries
        }
        
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():

    if not os.path.exists(RATINGS_FILE):
        if os.path.exists(SOURCE_FILE):
            print(f"{RATINGS_FILE} not found. Copying from {SOURCE_FILE}...")
            shutil.copy(SOURCE_FILE, RATINGS_FILE)
        else:
            print(f"File not found: {RATINGS_FILE} and source {SOURCE_FILE} is missing too.")
            return

    # Check headers to see if we need to add the new column
    with open(RATINGS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    headers_changed = False
    if "Main Actors" not in header:
        print("Adding 'Main Actors' column...")
        header.append("Main Actors")
        headers_changed = True
        
    if "Countries" not in header:
        print("Adding 'Countries' column...")
        header.append("Countries")
        headers_changed = True

    if headers_changed:
        # Add empty value to all existing rows for newly added columns
        # We need to be careful to match the index
        for row in rows:
            while len(row) < len(header):
                row.append("")
    
    actor_col_index = header.index("Main Actors")
    country_col_index = header.index("Countries")
    url_col_index = header.index("URL")
    
    processed_count = 0
    updated_rows = []
    
    try:
        updated_rows.append(header)
        for row in rows:
            # Ensure row has enough columns
            while len(row) < len(header):
                row.append("")
                
            current_actors = row[actor_col_index]
            current_countries = row[country_col_index]
            url = row[url_col_index]
            
            # We want to fetch if EITHER is missing, but efficient to do one request
            if (not current_actors or not current_countries) and url:
                metadata = get_metadata(url)
                if metadata:
                    if not current_actors:
                         row[actor_col_index] = metadata["Main Actors"]
                         print(f"Found actors: {metadata['Main Actors']}")
                    if not current_countries:
                         row[country_col_index] = metadata["Countries"]
                         print(f"Found countries: {metadata['Countries']}")
                    
                    processed_count += 1
                    # Polite delay
                    sleep_time = random.uniform(2, 5)
                    print(f"Sleeping for {sleep_time:.2f}s...")
                    time.sleep(sleep_time)
                else:
                    print(f"Could not find metadata for {url}")
            
            # updated_rows.append(row) # No longer needed
            
            # Save progress every 5 updates to avoid losing too much if stopped
            if processed_count > 0 and processed_count % 5 == 0:
                 print("Saving progress...")
                 with open(TEMP_FILE, 'w', encoding='utf-8', newline='') as f_out:
                    writer = csv.writer(f_out)
                    writer.writerows([header] + rows) 
                 shutil.copy(TEMP_FILE, RATINGS_FILE)

    except KeyboardInterrupt:
        print("Stopping early...")
    finally:
        # Final save
        print("Saving final changes...")
        with open(TEMP_FILE, 'w', encoding='utf-8', newline='') as f_out:
            writer = csv.writer(f_out)
            writer.writerows([header] + rows)
        shutil.move(TEMP_FILE, RATINGS_FILE)
        print("Done.")

if __name__ == "__main__":
    main()
