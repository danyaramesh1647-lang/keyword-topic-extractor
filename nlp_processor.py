"""Keyword and topic extraction with NLP.
Pipeline: sentence split -> tokenization -> POS tagging -> stop-word removal ->
candidate phrases -> TF-IDF scoring (sentences as documents) -> keywords ->
topic identification from domain vocabularies."""
import math
import re
from collections import Counter, defaultdict

import nltk

for path, pkg in [("tokenizers/punkt", "punkt"), ("tokenizers/punkt_tab", "punkt_tab"),
                  ("corpora/stopwords", "stopwords"),
                  ("taggers/averaged_perceptron_tagger_eng", "averaged_perceptron_tagger_eng")]:
    try:
        nltk.data.find(path)
    except LookupError:
        nltk.download(pkg, quiet=True)

from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize

stem = PorterStemmer().stem
STOP = set(stopwords.words("english")) | {
    "also", "can", "may", "many", "much", "one", "two", "use", "used", "using", "way",
    "thing", "things", "well", "like", "however", "therefore", "make", "makes", "made",
    "get", "gets", "even", "every", "among", "across", "around", "within",
    "today", "day", "year", "years", "time", "people", "world",
}
# noun-like -ing words allowed at the end of a phrase ("machine learning")
GERUNDS = {"learning", "computing", "engineering", "marketing", "processing", "programming",
           "banking", "training", "modeling", "mining", "networking", "farming",
           "manufacturing", "accounting", "planning", "testing", "streaming"}

NOUN = ("NN", "NNS", "NNP", "NNPS")
START_OK = NOUN + ("JJ",)
RUN_OK = START_OK + ("VBG", "VBN")
WORD_RE = re.compile(r"^[A-Za-z][A-Za-z\-]*$")

# topic -> domain vocabulary (matched on word stems)
TOPICS = {
    "Artificial Intelligence": "ai artificial intelligence machine learning algorithm neural network deep model robot automation chatbot nlp data prediction",
    "Healthcare": "health healthcare doctor patient disease medical medicine hospital treatment drug diagnosis therapy clinical surgery vaccine nurse symptom",
    "Education": "education student school teacher learning university college course classroom curriculum exam study academic training skill",
    "Business and Finance": "business company market finance financial investment investor bank revenue profit economy economic stock trade customer startup sales price",
    "Technology": "technology software hardware computer internet digital app application cloud device programming code website platform system network",
    "Cybersecurity": "security cybersecurity hacker attack malware encryption privacy password breach threat vulnerability firewall phishing",
    "Environment and Climate": "climate environment pollution carbon emission renewable solar energy forest wildlife sustainability warming ecosystem waste",
    "Science and Research": "science research scientist experiment study discovery laboratory physics chemistry biology space theory evidence",
    "Sports": "sport game team player match tournament coach league football cricket tennis athlete championship score",
    "Politics and Government": "government political election minister policy law parliament vote president democracy country public citizen",
    "Entertainment": "movie film music song actor actress cinema album series show concert festival celebrity",
    "Travel and Tourism": "travel tourism tourist trip hotel flight destination beach journey vacation airport visit",
    "Food and Nutrition": "food diet nutrition meal recipe restaurant cooking vitamin protein fruit vegetable kitchen",
}
TOPIC_STEMS = {name: {stem(w) for w in words.split()} for name, words in TOPICS.items()}


def _display(words):
    return " ".join(w if any(c.isupper() for c in w[1:]) else w.capitalize() for w in words)


def _candidates(sentences):
    """Noun phrases: (adjective|noun)* + noun head, 1 to 3 words, from POS tags."""
    found = []  # (stem_key, surface_words, sentence_index)
    for si, sent in enumerate(sentences):
        tagged = pos_tag(word_tokenize(sent))
        run = []
        for tok, tag in tagged + [("", ".")]:
            if WORD_RE.match(tok) and tok.lower() not in STOP and tag in RUN_OK \
                    and (len(tok) > 2 or tok.isupper()):
                run.append((tok, tag))
                continue
            for i in range(len(run)):
                for n in (1, 2, 3):
                    win = run[i:i + n]
                    if len(win) < n or win[0][1] not in START_OK:
                        continue
                    last = win[-1][1]
                    if last not in NOUN and not (n > 1 and win[-1][0].lower() in GERUNDS):
                        continue
                    words = [w for w, _ in win]
                    key = tuple(stem(w.lower()) for w in words)
                    found.append((key, words, si))
            run = []
    return found


def analyze(text, limit=12):
    text = re.sub(r"\s+", " ", text).strip()
    sentences = sent_tokenize(text)
    all_tokens = [t for t in word_tokenize(text) if WORD_RE.match(t)]
    surface_of = defaultdict(Counter)
    for t in all_tokens:
        surface_of[stem(t.lower())][t.lower()] += 1
    surface_of = {s: c.most_common(1)[0][0] for s, c in surface_of.items()}

    # --- TF-IDF on stems, every sentence is a "document" ---
    n_sent = len(sentences)
    df, tf = Counter(), Counter()
    for si, sent in enumerate(sentences):
        stems = [stem(t.lower()) for t in word_tokenize(sent)
                 if WORD_RE.match(t) and t.lower() not in STOP]
        df.update(set(stems))
        boost = 1.25 if si == 0 else 1.0
        for s in stems:
            tf[s] += boost
    word_score = {s: tf[s] * (math.log((n_sent + 1) / (df[s] + 1)) + 1) for s in tf}

    # --- candidate phrases and their scores ---
    counts, surfaces, first_pos = Counter(), defaultdict(Counter), {}
    for key, words, si in _candidates(sentences):
        counts[key] += 1
        surfaces[key][tuple(words)] += 1
        first_pos.setdefault(key, si)
    scored = []
    for key, freq in counts.items():
        avg = sum(word_score.get(s, 0) for s in key) / len(key)
        bonus = {1: 1.0, 2: 1.45, 3: 1.2}[len(key)]
        score = avg * bonus * (1 + 0.25 * math.log(freq))
        scored.append((score, key, freq))
    scored.sort(key=lambda x: (-x[0], first_pos[x[1]]))

    # --- pick top keywords, skip overlapping duplicates ---
    chosen = []
    for score, key, freq in scored:
        ks = set(key)
        if any(ks <= set(k) or set(k) <= ks for _, k, _ in chosen):
            continue
        chosen.append((score, key, freq))
        if len(chosen) == limit:
            break
    top = chosen[0][0] if chosen else 1
    keywords = [{
        "text": _display(surfaces[key].most_common(1)[0][0]),
        "count": freq,
        "relevance": round(score / top * 100),
    } for score, key, freq in chosen]

    return {
        "stats": {"words": len(all_tokens), "sentences": n_sent,
                  "unique_keywords": len(counts)},
        "keywords": keywords,
        "topics": _topics(word_score, keywords, surface_of),
    }


def _topics(word_score, keywords, surface_of):
    """Score each domain by the TF-IDF weight of the text words that match its vocabulary."""
    matches = []
    for name, stems in TOPIC_STEMS.items():
        hit = [x for x in word_score if x in stems]
        if hit:
            matches.append((sum(word_score[x] for x in hit), name, hit))
    matches.sort(reverse=True)

    topics, covered = [], set()
    if matches:
        top = matches[0][0]
        for score, name, hit in matches[:4]:
            if score / top < 0.2 and topics:
                continue  # ignore weak, accidental matches
            words = sorted(hit, key=lambda x: -word_score[x])[:5]
            topics.append({"name": name, "kind": "domain", "strength": round(score / top * 100),
                           "words": [surface_of.get(x, x).capitalize() for x in words]})
            covered |= set(hit)

    # fill remaining slots with multi-word keywords not already covered by a domain
    for kw in keywords:
        if len(topics) >= 5:
            break
        stems = {stem(w.lower()) for w in kw["text"].split()}
        if len(stems) > 1 and not stems <= covered:
            topics.append({"name": kw["text"], "kind": "theme",
                           "strength": kw["relevance"], "words": []})
            covered |= stems
    return topics