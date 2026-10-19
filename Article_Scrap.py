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
