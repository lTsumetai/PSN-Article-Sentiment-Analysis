# PSN News: Sentiment Analysis

The main objective of this project was to answer this specific question

when **Pasifik Satelit Nusantara (PSN)** makes the news, does the public take notice ?

this project scrapes news about PSN, finds what the coverage is about, checks how positive or negative it is, and compares it with google trends to see when and where people search for PSN's satellites

## Key Findings

1. articles / news scrap distribution using beautifulsoup was mostly informative. 53% neutral, 37% positive, 10% negative
2. the public searches for PSN satellites only around big events. each satellite keyword has exactly one big rise in searches and it sits in the month of a launch of a failure

   | Event | Search peak | Articles in that month | Average tone in that month |
   |---|---|---|---|
   | Nusantara Satu launch | Feb 2019 | 7 | +0.24 |
   | Nusantara Dua launch failure | Apr 2020 | 16 | -0.70 |
   | SATRIA | Jun 2023 | 10 | +0.23 |
   | Nusantara Lima launch | Sep 2025 | 39 | +0.48 |

3. The even months has more articles than a normal month. this means searches spikes when there is a burst of coverage, for example satellite launch
4. The even drives attention. launches were neutral to positive, and the nusantara dua failure was strongly negative.
5. 

## BERTopic


## Pipeline





## Data

| | |
|---|---|
| Articles | 193 (PSN-related, 190 mention PSN directly) |
| Sources | 75 publishers (detikInet 34, Bisnis Tekno 13, Kompas.id 10, Suara.com 10) |
| Period | May 2017 to July 2026 |
| Language | about 141 Indonesian, 52 English or other |
| Title only | 33 articles where the full text could not be scraped |

## Limitations



## How to Run


## Repository Structure



## Tech Stack

| | Tool | Used for |
|---|---|---|
| <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" alt="Python" width="24" height="24"/> | Python | Everything in the project |
| <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pandas/pandas-original.svg" alt="pandas" width="24" height="24"/> | pandas | Loading, cleaning and analyzing the data |
| <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/numpy/numpy-original.svg" alt="NumPy" width="24" height="24"/> | NumPy | Working with arrays, like the model's word weights |
| <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/scikitlearn/scikitlearn-original.svg" alt="scikit-learn" width="24" height="24"/> | scikit-learn | TF-IDF, Logistic Regression, Naive Bayes and tuning |
| 🇮🇩 | Sastrawi | Indonesian stopword list |
| <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/huggingface/huggingface-original.svg" alt="Hugging Face" width="24" height="24"/> | Hugging Face Transformers | Pretrained sentiment models (DistilBERT, XLM-RoBERTa) |
| <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pytorch/pytorch-original.svg" alt="PyTorch" width="24" height="24"/> | PyTorch | Running the pretrained models |
| <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/matplotlib/matplotlib-original.svg" alt="matplotlib" width="24" height="24"/> | matplotlib | Charts |
| <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/seaborn/seaborn-original.svg" alt="seaborn" width="24" height="24"/> | seaborn | Charts |

## Future Improvements
this project can be further improved by the following :
- Label more articles by hand, and train on them together with the pseudo-labels.
- Test the final model against the reference sample on articles it was not trained on.
- Collect more articles from scraping per publisher to compare sources more fairly.
