import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

def test_scrape(url):
    print(f"Testing URL: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test finding "Stars"
        stars = []
        label_span = soup.find('span', string='Stars') # Text lookup might need to be exact or contain
        if not label_span:
             print("Direct span 'Stars' not found, trying fuzzy...")
             label_span = soup.find('a', string='Stars')
        
        if label_span:
             print("Found 'Stars' label.")
             parent = label_span.find_parent('li')
             if parent:
                 links = parent.find_all('a', class_='ipc-metadata-list-item__list-content-item')
                 stars = [a.text.strip() for a in links]
        
        if not stars:
             print("Stars not found via metadata list. Trying top cast items...")
             cast_items = soup.select('div[data-testid="title-cast-item"] a[data-testid="title-cast-item__actor"]')
             stars = [a.text.strip() for a in cast_items[:3]]
             
        print(f"Extracted Stars: {stars}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test with Skyfall
    test_scrape("https://www.imdb.com/title/tt1074638")
