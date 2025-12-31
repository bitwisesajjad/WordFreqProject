# Word Frequency Analyzer & Corpus Tool

A sophisticated Python tool that analyzes text corpora to generate frequency lists for **Verbs**, **Nouns**, and **Adjectives**, and extracts common **Collocations (Phrases)**.

Unlike simple word counters, this project uses **Natural Language Processing (NLP)** (spaCy & NLTK) to understand context, lemmatize words (convert them to their root form), filter out "empty" grammatical words, and identify meaningful patterns like "Climate Change" or "Major Impact."

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

## Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/bitwisesajjad/WordFreqProject.git](https://github.com/bitwisesajjad/WordFreqProject.git)
    cd WordFreqProject
    ```

2.  **Create a virtual environment (Recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install spacy nltk
    ```

4.  **Download NLP Resources:**
    ```bash
    python -m spacy download en_core_web_sm
    ```
    *Note: The script will automatically download necessary NLTK data (stopwords, tokenizer) on the first run.*

## How to Use

### 1. Add Data
Place your text files (`.txt`) inside the **`Input_texts/`** folder.
* Note: You can add 300+ files at once, or add them gradually. The program handles both.

### 2. Run the Analyzer
Execute the main tool to process the text. This runs in two phases:
1.  **Frequency Analysis:** Updates word counts from *new* files.
2.  **Collocation Analysis:** Scans *all* files to find common phrases.

```bash
python corpus_tool.py

* **Output 1:** Updates `database/word_counts.json` (Word frequencies).
* **Output 2:** Creates/Updates `database/common_phrases.txt` (Top Bigrams & Trigrams).

### 3. View Frequency Results

To see the top ranked individual words (Nouns/Verbs/Adjectives) by frequency:

```bash
python view_results.py


WordFreqProject/
├── Input_texts/            # Place your .txt files here (Ignored by Git)
├── database/               # Stores the results (Ignored by Git)
│   ├── word_counts.json    # Frequency data
│   ├── common_phrases.txt  # Extracted phrases (Bigrams/Trigrams)
│   └── processed_log.json  # History of processed files
├── corpus_tool.py          # The core analysis engine (Freq + Collocations)
├── view_results.py         # Script to view top word lists
└── README.md               # Project documentation


# Logic Detail
Why "Quickly" = "Quick"? For vocabulary analysis, knowing that a student uses the concept of "quickness" is more important than the specific grammatical form. By converting adverbs to adjectives, we get a truer representation of the lexical range used in the text.

Why exclude "Be" verbs? Verbs like "is/are/was/were" appear in almost every sentence. Including them skews the frequency data and hides the more descriptive verbs (like analyze, construct, interpret) that we actually want to find.