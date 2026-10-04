# 🔑 Keyword & Topic Extractor

A Flask web app that reads an article or paragraph and automatically finds the most important keywords and phrases, their frequency, and the main topics. Built with NLTK, POS tagging and TF-IDF scoring.

## Features

- 📝 Large text input with a live word count
- 🔑 Keyword and key phrase extraction, shown as tags
- 📈 Keyword frequency bars
- 🧠 Main topic identification
- 📊 Number of words and sentences analyzed
- 📋 Copy results and 🧹 Clear buttons
- Example text for quick testing
- Responsive layout with light and dark mode

## How it works

```
User enters article/text
          ↓
    Text preprocessing (sentence split, tokenization)
          ↓
 POS tagging + stop-word removal
          ↓
    NLP analysis
       ↙       ↘
 Keywords     Topics
 (TF-IDF)     (domain vocabularies)
       ↓         ↓
  Important    Main
   phrases     subjects
```

1. The text is split into sentences and tokenized with NLTK.
2. Each word is tagged with its part of speech. Candidate phrases are built from adjectives and nouns (for example "medical images", "drug discovery").
3. Stop words are removed and words are reduced to stems with the Porter stemmer.
4. **TF-IDF** is calculated by treating every sentence as a document: words that are frequent in the text but concentrated in fewer sentences score higher. The first sentence gets a small boost.
5. Phrase scores are built from the word scores, longer phrases are preferred, and overlapping duplicates are removed.
6. **Topics** are identified by matching the weighted words against domain vocabularies (Healthcare, Artificial Intelligence, Environment, Business and more). Strong multi-word keywords fill the remaining topic slots.

## Example

**Input**
> Artificial intelligence is rapidly transforming healthcare. Machine learning algorithms can help doctors detect diseases earlier by analyzing medical images and patient data. AI-based systems are also being developed to improve drug discovery and provide personalized treatment.

**Output**

```
KEYWORDS
- Artificial Intelligence
- Machine Learning
- Medical Images
- Patient Data
- AI-based Systems
- Drug Discovery
- Healthcare

MAIN TOPICS
1. Healthcare
2. Artificial Intelligence
3. Medical Images
4. AI-based Systems
5. Drug Discovery
```

## NLP concepts demonstrated

Tokenization, POS tagging, stop-word removal, stemming, frequency analysis, TF-IDF, keyword extraction, topic identification.

## Tech stack

| Layer | Technology |
|-------|------------|
| Backend | Python, Flask |
| NLP | NLTK |
| Frontend | HTML, CSS, JavaScript |
| Deployment | Render, Gunicorn |

## Project structure

```
Keyword-Topic-Extractor/
│
├── app.py                 # Flask routes
├── nlp_processor.py       # preprocessing, TF-IDF, keywords, topics
├── requirements.txt
│
├── templates/
│   └── index.html
│
├── static/
│   ├── style.css
│   └── script.js
│
└── README.md
```

## Run locally

```bash
git clone https://github.com/danyaramesh1647-lang/keyword-topic-extractor.git
cd keyword-topic-extractor
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5050. NLTK downloads the data it needs (tokenizer, stop words, POS tagger) automatically on the first run.

## API

**POST** `/extract`

```json
{ "text": "Your article or paragraph here..." }
```

Returns statistics, keywords with counts and relevance, and the main topics.


## Limitations

- English text only.
- Works best on texts of 50 words or more. Very short texts give fewer keywords.
- Topics come from predefined domain vocabularies, so topics outside those domains appear as key phrases instead.
- It is not a trained topic model like LDA.

## Future improvements

- LDA topic modeling for large collections of documents
- Keyword extraction from PDF and URL input
- Export results as CSV

## Author

**Danya R**
GitHub: [danyaramesh1647-lang](https://github.com/danyaramesh1647-lang)