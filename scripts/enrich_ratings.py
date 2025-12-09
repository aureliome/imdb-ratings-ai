import csv
import time
import random
import requests
import os
import shutil
from bs4 import BeautifulSoup

RATINGS_FILE = '/Users/aureliomerenda/Dev/_am/cinema-ratings/ratings.csv'
TEMP_FILE = RATINGS_FILE + '.tmp'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

def get_main_actors(url):
    """
    Fetches the IMDb page and extracts main actors.
    """
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Strategy 1: Look for "Top Cast" section or similar.
        # IMDb structure varies, but often actors are linked with specific classes or roles.
        # Common pattern: check for specific IPC data attributes or list items.
        
        # Strategy 2: Look for the specific "Stars" section in the metadata block
        # Usually found near Director/Writers
        
        # Let's try a robust selector for the "Stars" or "Cast" section.
        # This selector targets the list of credits where "Stars" is usually listed.
        
        # New IMDb design often uses __NEXT_DATA__ json, but we try HTML parsing first.
        # Targeting the links inside the presentation list item for "Stars"
        
        # Attempt to find the "Stars" label and get siblings
        stars = []
        
        # Try finding specific data-testid which IMDb often uses now
        # "title-cast-item" is sometimes used for the full cast list, but we want the summary "Stars"
        
        # Search for the label "Stars"
        label_span = soup.find('span', string='Stars')
        if not label_span:
             label_span = soup.find('a', string='Stars')
             
        if label_span:
             # usually in a list item, we want the links following it
             parent = label_span.find_parent('li')
             if parent:
                 links = parent.find_all('a', class_='ipc-metadata-list-item__list-content-item')
                 stars = [a.text.strip() for a in links]
        
        if not stars:
             # Fallback: Try "Top Cast" section if "Stars" summary missing
             # This is harder to scrape reliably without rendering JS sometimes, but let's try
             # to find cast items.
             cast_items = soup.select('div[data-testid="title-cast-item"] a[data-testid="title-cast-item__actor"]')
             stars = [a.text.strip() for a in cast_items[:3]] # Take top 3
             
        return ", ".join(stars)
        
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def main():
    if not os.path.exists(RATINGS_FILE):
        print(f"File not found: {RATINGS_FILE}")
        return

    # Check headers to see if we need to add the new column
    with open(RATINGS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    if "Main Actors" not in header:
        print("Adding 'Main Actors' column...")
        header.append("Main Actors")
        # Add empty value to all existing rows for consistency before processing
        for row in rows:
            row.append("")
    
    actor_col_index = header.index("Main Actors")
    url_col_index = header.index("URL")
    
    processed_count = 0
    updated_rows = []
    
    # Write to temp file as we go, or write all at end?
    # Writing all at end is safer for atomic switch, but we want to be able to stop and resume.
    # Let's process 'rows' in memory and write to temp file incrementally if we wanted, 
    # but for simplicity, let's process and then save. 
    # Actually, the user said "movie-by-movie, no hurry". 
    # To support resuming, we should check if the field is empty.
    
    try:
        updated_rows.append(header)
        for row in rows:
            # Ensure row has enough columns (handle malformed rows if any, though csv module handles this mostly)
            while len(row) < len(header):
                row.append("")
                
            current_actors = row[actor_col_index]
            url = row[url_col_index]
            
            if not current_actors and url:
                actors = get_main_actors(url)
                if actors:
                    print(f"Found actors: {actors}")
                    row[actor_col_index] = actors
                    processed_count += 1
                    # Polite delay
                    sleep_time = random.uniform(2, 5)
                    print(f"Sleeping for {sleep_time:.2f}s...")
                    time.sleep(sleep_time)
                else:
                    print(f"Could not find actors for {url}")
            
            updated_rows.append(row)
            
            # Save progress every 5 updates to avoid losing too much if stopped
            if processed_count > 0 and processed_count % 5 == 0:
                 print("Saving progress...")
                 with open(TEMP_FILE, 'w', encoding='utf-8', newline='') as f_out:
                    writer = csv.writer(f_out)
                    writer.writerows(updated_rows + rows[len(updated_rows)-1:]) # Write current progress + remaining unprocessed
                 shutil.copy(TEMP_FILE, RATINGS_FILE)

    except KeyboardInterrupt:
        print("Stopping early...")
    finally:
        # Final save
        print("Saving final changes...")
        with open(TEMP_FILE, 'w', encoding='utf-8', newline='') as f_out:
            writer = csv.writer(f_out)
            writer.writerows(updated_rows)
        shutil.move(TEMP_FILE, RATINGS_FILE)
        print("Done.")

if __name__ == "__main__":
    main()
