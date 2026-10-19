

import re                                   
import time                                 
from datetime import date, timedelta        
from urllib.parse import quote_plus         

import feedparser
import requests                            
import pandas as pd                         
import trafilatura                          
from googlenewsdecoder import gnewsdecoder  




# Maximum number of articles to collect
MAX_ARTICLES = 150

# (3 years = 365 * 3 days)
DAYS_BACK = 365 * 10


CHUNK_DAYS = 90

# True  = also download the full article text 
# False = only keep the headline 
GET_FULL_TEXT = True

# csv output file 
OUTPUT_FILE = "psn_news.csv"

# lists for keywords
SEARCH_QUERIES = [
    '"Pasifik Satelit Nusantara"',
    '"PT Pasifik Satelit Nusantara"',
    '"PSN" satelit Indonesia',
    'PSN "Nusantara Lima"',
    'PSN "Nusantara Satu"',
    'PSN satelit internet desa',
    'PSN SATRIA satelit',
    'Adi Rahman Adiwoso',
    'PSN satelit Telkom',
    '"Pasifik Satelit Nusantara" satellite',
]

# Seconds to wait between requests. 
PAUSE_SECONDS = 1




def is_about_psn(text):
    text = text.lower()

    # Company name, satellite names, or founder to find relevancy
    if ("pasifik satelit" in text
            or "nusantara lima" in text
            or "nusantara satu" in text
            or "adi rahman adiwoso" in text):
        return True

    # adding context text 
    if "psn" in text and ("satelit" in text or "satellite" in text or "internet" in text):
        return True

    return False


#func to remove domain 
def clean_title(title):
   
    # r"\s+-\s+[^-]+$" means: "a dash near the end, followed by the source name"
    return re.sub(r"\s+-\s+[^-]+$", "", title)

#func to get clean title
def make_title_key(title):

    title = clean_title(title).lower()
    return re.sub(r"\W+", " ", title).strip()  # replace punctuation with spaces


#func to make time chunks time range
def make_time_chunks(start_date, end_date, chunk_days):

    chunks = []
    current = start_date
    while current < end_date:
        chunk_end = min(current + timedelta(days=chunk_days), end_date)
        chunks.append((current, chunk_end))
        current = chunk_end
    return chunks


#func to get real article link rather than google redirect link
def get_real_url(google_link):
 
    try:
        result = gnewsdecoder(google_link, interval=1)

        # Newer versions use "success", older versions use "status".
        # We check both so the code works either way.
        worked = result.get("success") or result.get("status")

        if worked:
            return result["decoded_url"]       # the real article link

        # If it really failed, print the whole result to see why
        print("   Decode failed:", result)

    except Exception as error:
        print("   Decode error:", error)

    return google_link                         # give up, use the original link

#func to download article content 
def get_article_text(url):

    # If the link is still a Google link, there is no article to read
    if "news.google.com" in url:
        return ""

    try:
        # Method 1: let trafilatura download the page
        html = trafilatura.fetch_url(url)

        # Method 2 using web browser
        if not html:
            response = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},  # browser-like name
                timeout=15,                             # give up after 15 seconds
            )

            # Status 200 means "OK". anything else gives error
            if response.status_code != 200:
                print(f"   Site said no (status {response.status_code}): {url[:60]}")
                return ""

            html = response.text

        # Pull the main text out of the page
        text = trafilatura.extract(html)
        return text or ""

    except Exception as error:
        print(f"   Could not get text: {error}")
        return ""


def search_google_news():
    """Search Google News and return a list of articles (basic info only)."""

    articles = []        # our collected articles will go in this list
    seen_titles = set()  # a "set" remembers titles we've already saved (no duplicates)

    # The time range we want to search
    today = date.today()
    start = today - timedelta(days=DAYS_BACK)

    # Newest chunks first, so recent news is collected before we hit the limit
    chunks = make_time_chunks(start, today + timedelta(days=1), CHUNK_DAYS)
    chunks.reverse()

    # Loop through every time chunk...
    for chunk_start, chunk_end in chunks:

        # ...and every search phrase
        for query in SEARCH_QUERIES:

            # Stop early if we already have enough articles
            if len(articles) >= MAX_ARTICLES:
                return articles

            # Add date limits to the search, Google understands "after:" and "before:"
            full_query = f"{query} after:{chunk_start} before:{chunk_end}"

            # Build the Google News RSS web address.
            # hl/gl/ceid = language and country (Indonesian, Indonesia)
            url = (
                "https://news.google.com/rss/search?q="
                + quote_plus(full_query)
                + "&hl=id&gl=ID&ceid=ID:id"
            )

            # Download and read the feed
            feed = feedparser.parse(url)

            # Each "entry" in the feed is one news article
            for entry in feed.entries:

                # Stop if we have enough
                if len(articles) >= MAX_ARTICLES:
                    return articles

                title = entry.get("title", "")
                key = make_title_key(title)

                # Skip empty titles and duplicates
                if key == "" or key in seen_titles:
                    continue

                # Skip articles that are not about PSN
                summary = entry.get("summary", "")
                print("CHECKING:", title)
                if not is_about_psn(title + " " + summary):
                    continue

                # This article is good! Remember it and save its info.
                seen_titles.add(key)
                articles.append({
                    "title": clean_title(title),
                    "source": entry.get("source", {}).get("title", ""),
                    "published": entry.get("published", ""),
                    "google_link": entry.get("link", ""),
                })

            time.sleep(PAUSE_SECONDS)  # short pause before the next search

        print(f"Searched {chunk_start} -> {chunk_end} | total so far: {len(articles)}")

    return articles



def main():
    print("Searching Google News...")
    articles = search_google_news()

    if len(articles) == 0:
        print("No articles found. Check your internet connection.")
        return

    print(f"\nFound {len(articles)} articles. Getting real links and text...\n")

    # For every article, find the real URL and (optionally) the full text
    for number, article in enumerate(articles, start=1):
        article["url"] = get_real_url(article["google_link"])

        if GET_FULL_TEXT:
            article["text"] = get_article_text(article["url"])
        else:
            article["text"] = ""

        print(f"[{number}/{len(articles)}] {article['source']} - {article['title'][:60]}")
        time.sleep(PAUSE_SECONDS)

    # Put everything into a table (DataFrame), like an Excel sheet
    df = pd.DataFrame(articles)

    # Convert the date text into a real date so we can sort by it
    df["published"] = pd.to_datetime(df["published"], errors="coerce", utc=True)

    # Create a column for sentiment analysis:
    # use the full text if we got a decent amount (more than 200 characters),
    # otherwise fall back to the headline.
    df["text_for_sentiment"] = df.apply(
        lambda row: row["text"] if len(row["text"]) > 200 else row["title"],
        axis=1,
    )

    # Sort newest first
    df = df.sort_values("published", ascending=False)

    # Save to CSV. "utf-8-sig" makes Excel display the characters correctly.
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"\nDone! Saved {len(df)} articles to '{OUTPUT_FILE}'")
    print(f"Articles with full text: {(df['text'].str.len() > 200).sum()}")


# This line means: "only run main() when I run this file directly".
# It's standard Python practice, you can just leave it as it is.
if __name__ == "__main__":
    main()