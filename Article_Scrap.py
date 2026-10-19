import re
import time

from datetime import date,timedelta
from urllib.parse import quote_plus


import feedparser
import requests
import pandas as pd
import trafilatura
from googlenewsdecoder import gnewsdecoder

### Scrapping Settings

max_articles = 150

#time to search
days_back = 365 * 10 # 10 years 

#time chunks in small searches ~100 per search
chunk_days = 90

#full text of the article 
# true = full article
# false = only the headlines
get_full_text = True

#file output csv name
output_file = "PSN_Articles.csv"

#lists of quotes or keywords 
search_queries = [
    '"Pasifik Satelit Nusantara"',
    '"PT Pasifik Satelit Nusantara"',
    '"PSN" satelit Indonesia',
    'PSN "Nusantara Lima"',
    'PSN "Nusantara Satu"',
    'PSN satelit internet desa',
    'PSN SATRIA satelit',
    'Adi Rahman Adiwoso',
    'PSN satelit Telkom',
    '"Pasifik Satelit Nusantara" satelite',
]

# delay to wait between requests
pause_seconds = 1

# Helper functions

# func to identify if its PSN
def is_about_psn(text):
    text = text.lower()

    # Company name, satellite name, or founder
    if("pasifik satelit" in text
            or "nusantara lima" in text
            or "nusantara satu" in text
            or "adi rahman adiwoso" in text):
        return True
    
    # psn mixed with said context
    if "psn" in text and ("satelit" in text or "satellite" in text or "internet" in text):
        return True

    return False

# funct to keep only the headline without domain
def clean_title(title):
    return re.sub(r"\s+-\s+[^-]+$", "", title)

#funct to detect duplicates
def make_title_key(title):
    title = clean_title(title).lower()
    return re.sub(r"\W+", " ", title).strip()

#funct to cut long period into smaller chunks
def make_time_chunks(start_date, end_date, chunk_days):

    chunks = []
    current = start_date
    while current < end_date:
        chunk_end = min(current + timedelta(days=chunk_days), end_date)
        chunks.append((current, chunk_end))
        current = chunk_end
    return chunks

#funct to get link by turning a google news redirect link into real article link
def get_real_url(google_link):
    try:
        result = gnewsdecoder(google_link, interval=1)

        worked = result.get("success") or result.get("status")

        if worked:
            return result["decoded_url"]

        print("  Decode failed:", result)

    except Exception as error:
        print("  Decode error", error)

    return google_link

#funct to get article context
def get_article_text(url):
    if "news.google.com" in url:
        return ""

    try:
        #downloading page with trafilatura
        html = trafilatura.fetch_url()

        if not html:
            response = requests.get(
                url,
                header={"User-Agent": "Mozilla/5.0"}
                timeout=15,
            )

            if response.status_code != 200:
                print(f"  site said no (status {response.status_code}): {url[:60]}")
                return ""

            html = response.text

        text = trafilatura.extract(html)
        return text or ""
    
    except Exception as error:
        print(f"  could not get text: {error}")
        return ""