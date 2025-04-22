"""
pip install requests beautifulsoup4 tqdm
python journal_crawler.py
"""

import requests
from bs4 import BeautifulSoup
import os
import json
import re
from pathlib import Path
from tqdm import tqdm
import concurrent.futures
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def sanitize_filename(filename):
    """Remove special characters that are invalid in filenames."""
    # Replace spaces with underscores and remove other invalid characters
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    sanitized = re.sub(r'\s+', "_", sanitized)
    # Limit filename length
    if len(sanitized) > 100:
        sanitized = sanitized[:97] + "..."
    return sanitized


def create_directory(directory_path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Created directory: {directory_path}")
    else:
        print(f"Directory already exists: {directory_path}")


def download_file(url, save_path, session):
    """Download file from URL and save to specified path."""
    try:
        # Use the provided session with retries and headers already set
        with session.get(url, stream=True) as response:
            response.raise_for_status()  # Raise exception for HTTP errors
            
            # Get file size for progress bar
            total_size = int(response.headers.get('content-length', 0))
            
            with open(save_path, 'wb') as file:
                # Download without tqdm progress bar for better performance in parallel downloads
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        file.write(chunk)
            
            return {'success': True, 'path': save_path, 'url': url}
    except Exception as e:
        return {'success': False, 'path': save_path, 'url': url, 'error': str(e)}


def extract_abstract(input_value):
    """Clean and extract the abstract from the input value."""
    # Remove HTML tags
    soup = BeautifulSoup(input_value, 'html.parser')
    text = soup.get_text()
    # Normalize spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def create_session():
    """Create a session with retry mechanism and browser-like headers."""
    session = requests.Session()
    
    # Set up retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Browser-like headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.soilsjournalnigeria.com/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    session.headers.update(headers)
    return session


def main():
    # URL to process
    url = input("Please Enter the URL: ")
    folder = input("Please Enter folder name: ")
    max_workers = 8  # Number of concurrent downloads
    
    # Create save directory in Downloads folder
    downloads_dir = str(Path.home() / "Downloads")
    volume_dir = os.path.join(downloads_dir, folder)
    create_directory(volume_dir)
    
    # Create a session for connection pooling
    session = create_session()
    
    # Fetch and parse the webpage
    print(f"Fetching content from {url}...")
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print("\nThe website is rejecting our request. Try accessing the site in your browser first.")
        return
    except requests.exceptions.ConnectionError:
        print("Connection Error: Failed to establish a connection to the website.")
        return
    except requests.exceptions.Timeout:
        print("Timeout Error: The request timed out. Try again later.")
        return
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return
    
    # Parse the page content and extract article data
    soup = BeautifulSoup(response.text, 'html.parser')
    metadata = []
    download_tasks = []
    
    # Process all articles at once to prepare download tasks
    topic_divs = soup.find_all("div", class_="topic")
    print(f"Found {len(topic_divs)} articles. Processing...")
    
    # Process each article to build metadata and prepare download tasks
    for i, topic_div in enumerate(topic_divs, 1):
        parent = topic_div.parent
        topic = topic_div.text.strip()
        print(f"\nProcessing article {i}/{len(topic_divs)}: {topic}")
        
        # Initialize article data
        article_data = {
            "topic": topic,
            "article_type": "",
            "pages": "",
            "authors": "",
            "abstract": "",
            "abstract_id": "",
            "download_link": "",
            "filename": sanitize_filename(topic) + ".pdf"
        }
        
        # Extract article type
        article_type_div = parent.find("div", class_="article_type")
        if article_type_div:
            article_data["article_type"] = article_type_div.text.strip()
        
        # Extract pages - direct attribute access is faster
        pages_div = parent.find("div", class_="pages")
        if pages_div:
            article_data["pages"] = pages_div.text.strip()
        
        # Extract authors
        authors_div = parent.find("div", class_="authors")
        if authors_div:
            article_data["authors"] = authors_div.text.strip()
        
        # Extract abstract
        abstract_input = parent.find("input", type="hidden")
        if abstract_input:
            article_data["abstract_id"] = abstract_input.get("id", "")
            article_data["abstract"] = extract_abstract(abstract_input.get("value", ""))
        
        # Find download link - more direct approach
        download_div = parent.find("div", class_="download")
        if download_div:
            # Try to find a link with download attribute first
            download_a = download_div.find("a", href=True, download=True)
            if not download_a:
                # If not found, take the first link
                download_a = download_div.find("a", href=True)
            
            if download_a:
                article_data["download_link"] = download_a.get("href", "")
        
        # Skip if no download link
        if not article_data["download_link"]:
            print(f"Warning: No download link found for article {i}: {topic}")
            continue
        
        # Create save path and prepare download task
        save_path = os.path.join(volume_dir, article_data["filename"])
        download_tasks.append((article_data, save_path))
        metadata.append(article_data)
    
    # Use ThreadPoolExecutor for parallel downloads
    print(f"\nDownloading {len(download_tasks)} PDFs in parallel (max {max_workers} concurrent downloads)...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Start all download tasks
        future_to_article = {
            executor.submit(
                download_file, 
                article_data["download_link"], 
                save_path, 
                session
            ): (article_data, i) 
            for i, (article_data, save_path) in enumerate(download_tasks)
        }
        
        # Process results as they complete
        for future in tqdm(concurrent.futures.as_completed(future_to_article), 
                          total=len(future_to_article),
                          desc="Downloading articles"):
            article_data, i = future_to_article[future]
            try:
                result = future.result()
                if result['success']:
                    print(f"Downloaded: {article_data['topic']}")
                else:
                    print(f"Error downloading {article_data['topic']}: {result['error']}")
            except Exception as e:
                print(f"Error processing {article_data['topic']}: {str(e)}")
    
    # Save metadata to JSON file
    json_path = os.path.join(volume_dir, "metadata.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\nComplete! Processed {len(metadata)} articles.")
    print(f"Metadata saved to {json_path}")

if __name__ == "__main__":
    main()