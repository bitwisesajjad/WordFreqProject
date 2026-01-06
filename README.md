# Word Frequency Analyzer & Corpus Tool

A Python tool that analyzes text corpora to generate frequency lists for **Verbs**, **Nouns**, and **Adjectives**, and extracts common **Collocations (Phrases)**.

Unlike simple word counters (which are basically just fancy `wc -w`), this project uses **Natural Language Processing (NLP)** (spaCy & NLTK) to understand context, lemmatize words (convert them to their root form), filter out "empty" grammatical words, and identify meaningful patterns like "climate change" or "major impact."

## Key Features

* **Smart Lemmatization:**
    * Counts "eating," "ate," and "eats" as a single entry: **eat**.
    * Counts "books" and "book" as a single entry: **book**.
* **Adverb Normalization:**
    * Automatically converts Adverbs to their Adjective roots.
    * Example: "Quickly" counts towards the frequency of **"quick"**.
* **Phrase Extraction (Collocations):**
    * Uses statistical analysis (Likelihood Ratio) to find words that "stick together."
    * Extracts meaningful **Bigrams** (2-word phrases) and **Trigrams** (3-word phrases).
* **Intelligent Filtering (White List):**
    * Strictly keeps only **Nouns**, **Verbs**, and **Adjectives**.
    * Automatically ignores pronouns, prepositions, conjunctions, and punctuation.
* **Incremental Processing:**
    * Maintains a `processed_log.json` history.
    * You can add new text files to the folder later, and the program will **only** process the new files for frequency counts without recounting the old ones.
    * Now detects file changes - if you edit a file, it'll rebuild the counts automatically.

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/bitwisesajjad/WordFreqProject.git
    cd WordFreqProject
    ```

2. **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies:**
    ```bash
    pip install spacy nltk
    ```

4. **Download NLP Resources:**
    ```bash
    python -m spacy download en_core_web_sm
    ```
    *Note: The script will automatically download necessary NLTK data (stopwords, tokenizer) on the first run.*

## How to Use

### 1. Add Data
Put your text files (`.txt`) inside the **`Input_texts/`** folder.
* You can add 300+ files at once, or add them gradually. The program handles both.
* Pro tip: don't add War and Peace unless you have time for a coffee break

### 2. Run the Analyzer
Execute the main tool to process the text. This runs in two phases:
1. **Frequency Analysis:** Updates word counts from *new* files.
2. **Collocation Analysis:** Scans *all* files to find common phrases.

```bash
python corpus_tool.py
```

* **Output 1:** Updates `database/word_counts.json` (Word frequencies).
* **Output 2:** Creates/Updates `database/common_phrases.txt` (Top Bigrams & Trigrams).

### 3. View Frequency Results

To see the top ranked individual words (Nouns/Verbs/Adjectives) by frequency:

```bash
python view_results.py
```

## Project Structure

```
WordFreqProject/
├── Input_texts/            # place your .txt files here (ignored by git)
├── database/               # stores the results (ignored by git)
│   ├── word_counts.json    # frequency data
│   ├── common_phrases.txt  # extracted phrases (bigrams/trigrams)
│   └── processed_log.json  # history of processed files + timestamps
├── corpus_tool.py          # the core analysis engine
├── view_results.py         # script to view top word lists
└── README.md               # you're reading it
```

## Logic Details

**Why "Quickly" = "Quick"?**
For vocabulary analysis, knowing that a student uses the concept of "quickness" is more important than the specific grammatical form. By converting adverbs to adjectives, we get a truer representation of the lexical range used in the text. (Also, linguists probably have opinions about this, but it works.)

**Why exclude "Be" verbs?**
Verbs like "is/are/was/were" appear in almost every sentence. Including them skews the frequency data and hides the more descriptive verbs (like analyze, construct, interpret) that we actually want to find. Nobody needs a tool to tell them "is" is common.

## Changelog

### 2026-01-06 - timestamp detection & rebuild logic
* Added timestamp detection - now tracks modification times of files
* Refactored the update logic: if a file modification is detected, we trigger a full rebuild
* Updated log file format to store `mtime` instead of just filenames
* Fixed a bug where the migration script would crash on empty JSON (whoops)

### 2026-01-01 - project renamed and expanded to collocations
* Expanded the original idea from only word-frequency counting to also finding common bigrams and trigrams (collocations)
* Added Phase 2 using NLTK collocation finders to extract frequent 2-word and 3-word phrases
* Updated the overall project purpose to be both frequency analysis and phrase discovery, not just counting words anymore
* Cleaned up the processing pipeline so Phase 1 (frequencies) and Phase 2 (collocations) both run together as part of the main script

### 2026-01-01 - initial version: basic word frequency counter
* Created the first version of the project as a simple word frequency counter
* The goal at this stage was only to process text files and count lemmas for nouns, verbs, and adjectives
* Implemented ignored-word filtering and basic normalization using spaCy
* The project could already store results into JSON and keep track of processed files

## Future Improvements

**Reprocess changed files automatically**
* Want to detect when a file has been edited and reprocess it instead of ignoring it. Probably use timestamps or file hashes and update the counts intelligently.
* UPDATE: this is now done as of 2026-01-06

**Add per-document statistics**
* Want to see frequencies not only globally, but also per file. This will let me compare texts and understand how vocabulary changes across documents.

**Turn the script into a real command-line tool**
* Want to run this with flags like `--update` or `--phrases` so I don't have to edit the code every time. This will also teach me proper CLI design.

**Export human-readable reports**
* Want to generate Markdown or CSV summaries of the most common words and phrases. The idea is to make the tool produce something I can open and read directly.

**Custom stopword configuration**
* Want to move stopwords into a user-editable file and let myself add or remove words easily. This will make the project more flexible instead of everything being hardcoded.

**Add visualizations like word clouds or bar charts**
* Want to visualize the most frequent words so I can actually see the results instead of only reading JSON. This will also get me more comfortable with plotting libraries.
* Basically I want pretty pictures because staring at JSON hurts my eyes

**Raw word mode vs lemma mode**
* Want to add a switch so I can count either raw words or lemmas. That way I can explore how much lemmatization actually changes the results.

**Part-of-speech statistics**
* Want to calculate how many nouns, verbs, and adjectives appear and show simple percentages or charts. This will help me understand the grammatical profile of the corpus.

**General n-gram explorer**
* Want to let the user choose any n value instead of only bigrams and trigrams. This will turn the phrase finder into a more general tool.

**Multi-language support**
* Want to experiment with other spaCy language models and switch languages through configuration. This will push me to think about tokenization and stopwords beyond English.
* Also maybe I'll finally learn what those German compound nouns are doing