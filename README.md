# PSN News: Sentiment Analysis

The main objective of this project was to answer this specific question

when **Pasifik Satelit Nusantara (PSN)** makes the news, does the public take notice ?

this project scrapes news about PSN, finds what the coverage is about, checks how positive or negative it is, and compares it with google trends to see when and where people search for PSN's satellites

## Key Findings

1. articles / news scrap distribution using beautifulsoup was mostly informative. 53% neutral, 37% positive, 10% negative
2. the public searches for PSN satellites only around big events. each satellite keyword has exactly one big rise in searches and it sits in the month of a launch of a failure

   | Event | Search peak | Articles in that month | Average drivers in that month |
   |---|---|---|---|
   | Nusantara Satu launch | Feb 2019 | 7 | +0.24 |
   | Nusantara Dua launch failure | Apr 2020 | 16 | -0.70 |
   | SATRIA | Jun 2023 | 10 | +0.23 |
   | Nusantara Lima launch | Sep 2025 | 39 | +0.48 |

3. The even months has more articles than a normal month. this means searches spikes when there is a burst of coverage, for example satellite launch
4. The even drives attention. launches were neutral to positive, and the nusantara dua failure was strongly negative.
5. The most negative topic occurred during the month of the Nusantara Dua failure, with a sentiment score of -0.61. meanwhile the rest of the topic was mostly dominant positive or neutral. this shows that sentiment highly dependant on topics.
6. 

## BERTopic

Average sentiment goes from negative to positive. topics with fewer than 10 articles are left out of the table.

| Topic | Articles | Average sentiment |
|---|---|---|
| Nusantara Dua launch failure | 18 | -0.61 |
| Orbit slots and Starlink | 29 | 0.11 |
| SATRIA project | 38 | 0.21 |
| Satellite launch and capacity | 26 | 0.23 |
| Adi Rahman Adiwoso (CEO) | 20 | 0.38 |
| Nusantara Lima launch | 59 | 0.39 |
| Nusantara Lima capacity and connectivity | 21 | 0.47 |
| Digital technology and connectivity | 13 | 0.55 |
| Rural internet access | 12 | 0.61 |


## Pipeline

```
Scraping → Cleaning → Topic Modelling → Topic Grouping → Google Trends Analysis
→ Sentiment Analysis → Insights & Findings
```

## Approach

News articles and google trends are two seperate tables, so they are joined by **month** column. each article gets the search numbers of the month it was published in.

- topic will be used to search for google trend keywords, and topic will be grouped based on the topic generated.
- Google trends cannot filter news or article that talks about psn, so General topics are excluded, for example Rural Internet Access
- Google trends analysis where there are months  where the search score went up compared with the previous month and a month where a topic group had more articles.
- plotting region maps where google trends score was based in. google trend scores are joined to a GeoJSON file of indoneisa's provinces by province name and visualized with map and a heatmap
- Three Classifiers were used to predict sentiment for each articles. then are compared with 5-fold cross-validation on the hand labelled articles. the best one will be used for predicting the remaining articles.

| Model | Macro F1 | Accuracy |
|---|---|---|
| TF-IDF + Logistic Regression | 0.743 | 0.761 |
| TF-IDF + SVM | 0.698 | 0.722 |
| TF-IDF + Naive Bayes | 0.690 | 0.722 |



## Data

| | |
|---|---|
| Articles | 918 scraped from Google News RSS, 254 after cleaning (249 used for Trends and sentiment, after removing 5 articles about "Proyek Strategis Nasional") |
| Sources | detikInet 49, Bisnis Tekno 25, Kompas.id 20, Suara.com 12 (top 4, of the 249 articles) |
| Period | May 2017 to July 2026 |
| Language | 216 Indonesian, 38 English |
| Article length | median 417 words |
| Hand labels | 180 articles (24 negative, 92 neutral, 64 positive) |
| Google Trends | monthly scores for 5 keywords, plus region tables by province (13 to 27 provinces for Nusantara Satu and SATRIA, 4 to 6 for the rest) |

## Limitations

- every satelite keyword only has one big search rise, hence the pattern only comes ffrom 4 cases
- Coverage and searches spikes together, but only a certain event drives them both.
- The dataset used (after cleaning) was only 254 articles, being several topics only has 12 to 21 articles, and the negative sentiment only has just 24 hand labels
- Google News RSS gives uneven coverage by year. making it imbalanced data.
- f1 score for the best model is 0.74 in cross-validation, it less accurate on english articles rather than indonesian one, english article scores 0.67 meanwhile indonesian ones is at 0.78. it can be improved by using another prediction model.
 

## Repository Structure

```
├── Topic_Modelling_Sentiment_Analysis.ipynb   
├── psn_news_scraped.csv                      
├── psn_article_cleaned.csv                   
├── psn_to_label.csv                          
├── GoogleTrends/                             
│   ├── satelit_*.csv                         
│   └── trends_*.csv                          
├── GoogleTrendsRegion/                      
├── GeoJSON/
│   └── indonesia_provinces.geojson           
└── README.md
```


## Tech Stack

| | Tool | Usage |
|---|---|---|
| <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" alt="Python" width="24" height="24"/> | Python | Everything in the project |
| <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/jupyter/jupyter-original.svg" alt="Jupyter" width="24" height="24"/> | Jupyter Notebook | Running and documenting the analysis |
| <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pandas/pandas-original.svg" alt="pandas" width="24" height="24"/> | pandas | Loading, cleaning and joining the data |
| <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/numpy/numpy-original.svg" alt="NumPy" width="24" height="24"/> | NumPy | Working with arrays, like the article embeddings |
| 🧩 | BERTopic | Topic modelling (UMAP, HDBSCAN and c-TF-IDF) |
| <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/huggingface/huggingface-original.svg" alt="Hugging Face" width="24" height="24"/> | Sentence-Transformers | Multilingual article embeddings (paraphrase-multilingual-MiniLM-L12-v2) |
| <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pytorch/pytorch-original.svg" alt="PyTorch" width="24" height="24"/> | PyTorch | Running the embedding model |
| <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/scikitlearn/scikitlearn-original.svg" alt="scikit-learn" width="24" height="24"/> | scikit-learn | TF-IDF, Logistic Regression, Naive Bayes, SVM and cross-validation |
| 🇮🇩 | Sastrawi | Indonesian stopword list |
| 📈 | Google Trends | Search interest over time and by province |
| <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/plotly/plotly-original.svg" alt="Plotly" width="24" height="24"/> | Plotly | Interactive province map |
| 🗺️ | GeoJSON | Province outlines for the map |
| <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/matplotlib/matplotlib-original.svg" alt="matplotlib" width="24" height="24"/> | matplotlib | Charts |
| <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/seaborn/seaborn-original.svg" alt="seaborn" width="24" height="24"/> | seaborn | Charts |

## Future Improvements
this project can be further improved by the following:
- Label more articles by hand, especially negative ones.
- Comparing PSN's Search interest with a competitor such as starlink. 
- export region data with  a wider date range or broader search terms, not based on topics. so it will get more provinces for nusantara dua, nusantara lima, and PSN's CEO.
- topic stemming on topics generated by BERTopic where the context isn't about PSN
