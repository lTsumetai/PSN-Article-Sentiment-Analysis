# PSN News Sentiment Analysis

How does the news talk about **Pasifik Satelit Nusantara (PSN)**.

## Key Findings



## Pipeline


## Approach: Pseudo-labeling





## Data

| | |
|---|---|
| Articles | 193 (PSN-related, 190 mention PSN directly) |
| Sources | 75 publishers (detikInet 34, Bisnis Tekno 13, Kompas.id 10, Suara.com 10) |
| Period | May 2017 to July 2026 |
| Language | about 141 Indonesian, 52 English or other |
| Title only | 33 articles where the full text could not be scraped |

## Limitations

- **The labels come from a model.** Every score for the student model is learnt from DistilBERT, not accuracy.
- **Positive is probably overcounted.** In the 80-article reference sample, 53% of articles were neutral and 38% positive, but DistilBERT called almost nothing neutral. News is mostly factual, so the real distribution of neutral articles is likely much higher than the 1% shown.
- **Neutral is almost missing.** Only 2 articles are labeled neutral, so the student model cannot learn that class.
- **Small data.** With 193 articles, and only 5 to 34 articles per publisher, differences between sources could be chance.
- **Some labels are incorectly predicted.** A few articles about a successful launch are labeled negative, for example titles with "Berhasil Mengangkasa".
- **Coverage gaps.** Google News RSS gives uneven coverage by year (for example, no articles in 2018).
- **Reference labels are small and title-based.** The 80-article sample was labeled from titles only, so it is a rough check.
- **Unstable cross-validation score.** Only 2 articles are neutral, so some cross-validation folds contain none, and the f1 score differs alot with small changes (0.633 before stopword removal, 0.612 after).

## How to Run


## Repository Structure

```
├── Article_Scrap.py                 # scrapes Google News RSS into PSN_articles.csv
├── Data_Checking.ipynb              # quick data check after scraping
├── PSN_articles.csv                 # 193 scraped PSN articles (output of the script)
├── labeled_sample.csv               # 80-article reference sample
├── Article_Sentiment_Analysis.ipynb # labeling, modelling and analysis
└── README.md
```

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
