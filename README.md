# PSN News Sentiment Analysis

How does the news talk about **Pasifik Satelit Nusantara (PSN)**. This project scrapes news articles, labels their sentiment with a pretrained model, trains a Logistic Regression model on those labels, and analyzes how sentiment changes over time and across publishers.

The scraped articles have no sentiment labels, so the project uses **pseudo-labeling**, a teacher-student approach. a pretrained transformer labels the data, and a classic ML model learns from those labels.

## Key Findings

- **Overall sentiment:** 161 of 193 articles are labeled positive (83%), 30 negative (16%) and 2 neutral (1%). The positive distribution is high, because the labeler model almost never predicts neutral (see [Limitations](#limitations)).
- **Sentiment follows events:** negative articles is not evenly distributed.
  - **April 2020:** 16 negative articles in 6 days, all about the Nusantara Dua satellite failing to reach orbit.
  - **September 2025:** a cluster of negative articles around the delays before the Nusantara Lima launch.
- **Publishers:** Kompas.com has the highest share of negative articles (4 of 6), but the sample is small to say a publisher is more negative. detikInet has the most negative articles (7), but that is only 21% of its 34 articles.
- **Top words:** after removing English and Indonesian stopwords, the words that push an article toward each label are still mostly events and company names. eg. *palapa*, *mengangkasa*, *scrub* for negative and *kapasitas*, *terbesar*, *teknologi* for positive, not emotion words.

## Pipeline

1. **Scraping and quick check:** collect PSN articles from Google News RSS (`Article_Scrap.py`), then run a quick check on the scraped file (`Data_Checking.ipynb`).
2. **EDA and cleaning:** check duplicates, dates, sources, language and text length, then clean the article text.
3. **Pseudo-labeling:** compare two pretrained sentiment models and label every article with the better one (DistilBERT).
4. **Modelling:** train Logistic Regression and Naive Bayes on the pseudo-labels as a baseline, then remove English and Indonesian stopwords and tune Logistic   Regression with `GridSearchCV`.
5. **Sentiment analysis:** use the final Logistic Regression model to answer four questions
   - overall sentiment
   - change over time
   - differences between sources 
   - which words drives the sentiment.

## Approach: Pseudo-labeling

```
unlabeled articles ──> DistilBERT (teacher) ──> pseudo-labels ──> Logistic Regression (student)
```

- **Teacher:** `lxyuan/distilbert-base-multilingual-cased-sentiments-student`, a multilingual model that handles both Indonesian and English articles.
- **Student:** a TF-IDF + Logistic Regression pipeline trained on the teacher's labels. The final tuned model removes English (scikit-learn) and Indonesian ([Sastrawi](https://github.com/har07/PySastrawi)) stopwords.

Pseudo-labels are not ground truth. The student's scores show how closely it copies the teacher, not how correct the sentiment is.

### Choosing the labeler

Two pretrained models were compared on an 80-article reference sample, labeled manually from article titles:

| Model | Accuracy | Macro F1 | Negative found | Positive found | Neutral found |
|---|---|---|---|---|---|
| DistilBERT (`lxyuan`) | 0.44 | 0.44 | 7 of 8 | 28 of 30 | 0 of 42 |
| XLM-RoBERTa (`cardiffnlp`) | 0.55 | 0.41 | 2 of 8 | 3 of 30 | 39 of 42 |

DistilBERT finds most positive and negative articles but almost never says neutral. XLM-RoBERTa does the opposite, labeling almost everything neutral. DistilBERT was chosen because it separates positive from negative far better, and that matters more for sentiment analysis.

### Student model results

Test set, consist of 39 articles (32 positive, 7 negative, 0 neutral), split 80/20 with stratification.

| Model | Accuracy | Macro F1 |
|---|---|---|
| Logistic Regression | 0.923 | 0.841 |
| Naive Bayes | 0.821 | 0.451 |

Naive Bayes predicts "positive" for every article, so it finds none of the negative ones. Logistic Regression finds 4 of the 7. These two scores are a baseline without stopword removal. Logistic Regression was then tuned with stopword removal and `GridSearchCV` with the best param `C=10`, `max_features=2000`, `ngram_range=(1, 1)`, that produces cross-validation f1 score at 0.612 and used as the final model.

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

```bash
git clone https://github.com/lTsumetai/PSN-Article-Sentiment-Analysis
cd PSN-Article-Sentiment-Analysis
pip install pandas numpy matplotlib seaborn scikit-learn torch transformers Sastrawi
jupyter notebook Article_Sentiment_Analysis.ipynb
```

- The notebook reads `PSN_articles.csv` and `labeled_sample.csv`, so keep them in the same folder.
- The pretrained models are downloaded from Hugging Face on the first run. Labeling 193 articles on a CPU may take a few minutes.
- To collect fresh articles, run `Article_Scrap.py` (its imports are listed at the top of the file). It writes `PSN_articles.csv`. Then open `Data_Checking.ipynb` for a quick check of the scraped data before using it in the main notebook.

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
