# Web Scraping Tool

This Python-based Web Scraping Tool allows you to scrape data from multiple websites and extract useful information such as titles, headings, links, and images. It saves the scraped data into a CSV file for easy access and analysis. This tool respects robots.txt to avoid scraping pages that are disallowed.

## Features

- Scrape titles, headings, links, and images from websites.
- Supports scraping multiple pages from a list of URLs or a sitemap XML.
- Automatically retries failed requests up to 3 times.
- Respects the `robots.txt` file to ensure ethical scraping.
- Saves scraped data to a CSV file for easy access.
- Uses a random User-Agent to avoid being blocked by websites.

## Requirements

To use this tool, make sure you have the following Python libraries installed:

- `requests`
- `beautifulsoup4`
- `fake-useragent`

You can install these dependencies by running:

```bash
pip install requests beautifulsoup4 fake-useragent
