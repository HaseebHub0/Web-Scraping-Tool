import os
import time
import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin, urlparse
from fake_useragent import UserAgent
from requests.exceptions import RequestException

# User-Agent for HTTP requests (avoids blocking)
ua = UserAgent()

# Function to get a valid User-Agent
def get_headers():
    return {
        'User-Agent': ua.random
    }

# Function to check if a URL is valid
def is_valid_url(url):
    """
    Checks if the URL is valid by parsing it using urlparse.
    """
    parsed_url = urlparse(url)
    return bool(parsed_url.netloc) and bool(parsed_url.scheme)

# Function to handle retries in case of request failure
def get_page(url, retries=3):
    """
    Tries to fetch the content of the page, retries on failure.
    """
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
        return response.text
    except RequestException as e:
        if retries > 0:
            print(f"Error fetching {url}, retrying... {retries} attempts left.")
            time.sleep(2)
            return get_page(url, retries - 1)
        else:
            print(f"Failed to retrieve {url}: {e}")
            return None

# Function to parse the page content
def parse_page(content, base_url):
    """
    Parse the content of the page and extract titles, headings, links, and images.
    """
    soup = BeautifulSoup(content, 'html.parser')
    
    page_data = {
        'url': base_url,
        'title': soup.title.string if soup.title else 'No Title',
        'headings': [],
        'links': [],
        'images': []
    }
    
    # Extract headings (h1, h2, h3, etc.)
    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        page_data['headings'].append(heading.get_text(strip=True))
    
    # Extract all links
    for link in soup.find_all('a', href=True):
        link_url = urljoin(base_url, link['href'])
        if is_valid_url(link_url):
            page_data['links'].append(link_url)
    
    # Extract all images
    for img in soup.find_all('img', src=True):
        img_url = urljoin(base_url, img['src'])
        if is_valid_url(img_url):
            page_data['images'].append(img_url)
    
    return page_data

# Function to scrape a list of URLs
def scrape_urls(urls, output_file='scraped_data.csv'):
    """
    Scrape multiple URLs and save the extracted data to a CSV file.
    """
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['url', 'title', 'headings', 'links', 'images']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for url in urls:
            print(f"Scraping {url}...")
            content = get_page(url)
            if content:
                data = parse_page(content, url)
                writer.writerow({
                    'url': data['url'],
                    'title': data['title'],
                    'headings': ', '.join(data['headings']),
                    'links': ', '.join(data['links']),
                    'images': ', '.join(data['images'])
                })
                print(f"Data for {url} saved.")
            time.sleep(1)  # Sleep between requests to avoid overloading the server

# Function to extract URLs from a sitemap.xml
def extract_urls_from_sitemap(sitemap_url):
    """
    Extracts URLs from a sitemap file.
    """
    sitemap_content = get_page(sitemap_url)
    if sitemap_content:
        soup = BeautifulSoup(sitemap_content, 'xml')
        urls = [loc.get_text() for loc in soup.find_all('loc')]
        return urls
    else:
        return []

# Function to respect robots.txt
def can_scrape_url(url):
    """
    Checks robots.txt to see if scraping is allowed on the URL.
    """
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    robots_content = get_page(robots_url)
    
    if robots_content:
        soup = BeautifulSoup(robots_content, 'html.parser')
        # This is a simple check; more complex logic can be added to fully parse robots.txt
        if "Disallow: /" in robots_content:
            return False
    return True

# Function to scrape and save data from a list of URLs or a sitemap
def scrape_and_save(url_list_or_sitemap, output_file='scraped_data.csv'):
    """
    Scrapes URLs from a list or sitemap and saves the result in a CSV file.
    """
    urls = []
    
    if url_list_or_sitemap.startswith('http') and url_list_or_sitemap.endswith('.xml'):
        # It's a sitemap URL
        print(f"Extracting URLs from sitemap {url_list_or_sitemap}...")
        urls = extract_urls_from_sitemap(url_list_or_sitemap)
    else:
        # It's a list of URLs
        urls = url_list_or_sitemap
    
    # Filter out URLs that can't be scraped based on robots.txt
    valid_urls = [url for url in urls if can_scrape_url(url)]
    
    if valid_urls:
        print(f"Found {len(valid_urls)} valid URLs to scrape.")
        scrape_urls(valid_urls, output_file)
    else:
        print("No valid URLs found to scrape.")

# Main function to execute the scraper
def main():
    """
    Main function to execute the web scraping tool.
    """
    # Example list of URLs to scrape
    urls_to_scrape = [
        "https://example.com", 
        "https://anotherexample.com"
    ]
    
    # Uncomment the line below to use a sitemap instead
    # urls_to_scrape = "https://example.com/sitemap.xml"
    
    # Call scrape_and_save to scrape data
    scrape_and_save(urls_to_scrape)

if __name__ == "__main__":
    main()
