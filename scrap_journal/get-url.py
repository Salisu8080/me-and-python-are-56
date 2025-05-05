import requests
from bs4 import BeautifulSoup
import csv
import re

# Target URL
base_url = "https://www.soilsjournalnigeria.com/view-articles.php"

# Add headers to mimic a real browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36'
}

# Send request with headers
response = requests.get(base_url, headers=headers)
response.raise_for_status()  # Will raise if request fails

# Parse HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Extract volume links
volume_links = []
for a_tag in soup.find_all('a', href=True):
    href = a_tag['href']
    if 'volume-list.php?volume=' in href:
        full_url = f"https://www.soilsjournalnigeria.com/{href}"
        volume_param = href.split('=')[1]
        cleaned = re.sub(r'[^\w]+', '-', volume_param).strip('-').lower()
        cleaned = cleaned.replace('--', '-')
        volume_links.append([full_url, f"volume{cleaned}"])

# Save to CSV
with open('soilsjournal_volumes.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['url', 'volume-issue'])
    writer.writerows(volume_links)

print("✅ Scraping complete. Data saved to 'soilsjournal_volumes.csv'.")
