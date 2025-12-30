# Word Frequency Analyzer & Corpus Tool

A sophisticated Python tool that analyzes texts to generate frequency lists for **Verbs**, **Nouns**, and **Adjectives**.

Unlike simple word counters, this project uses **Natural Language Processing (NLP)** to understand context, lemmatize words (convert them to their root form), and filter out "empty" grammatical words.

## Key Features

* **Smart Lemmatization:**
    * Counts "eating," "ate," and "eats" as a single entry: **eat**.
    * Counts "books" and "book" as a single entry: **book**.
* **Adverb Normalization:**
    * Automatically converts Adverbs to their Adjective roots.
    * Example: "Quickly" counts towards the frequency of **"quick"**.
* **Intelligent Filtering (White List):**
    * Strictly keeps only **Nouns**, **Verbs**, and **Adjectives**.
    * Automatically ignores pronouns, prepositions, conjunctions, and punctuation.
* **Custom "Stop List":**
    * Filters out trivial "functional" verbs (is, are, was, have, do).
    * (Optional) Filters out generic descriptors (good, bad, big) to focus on meaningful vocabulary.
* **Incremental Processing:**
    * Maintains a `processed_log.json` history.
    * You can add new text files to the folder later, and the program will **only** process the new files without recounting the old ones.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/bitwisesajjad/WordFreqProject.git
    cd WordFreqProject
    ```

2.  **Create a virtual environment (Recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install spacy
    ```

4.  **Download the NLP Language Model:**
    This project uses the English Core Web Small model from spaCy.
    ```bash
    python -m spacy download en_core_web_sm
    ```

## How to Use

### 1. Add Data
Place your text files (`.txt`) inside the **`Input_texts/`** folder.
* Note: You can add 300+ files at once, or add them gradually. The program handles both.

### 2. Run the Analyzer
Execute the main script to process the text files and build/update the database.
```bash
python main.py
```
* Output: This updates `database/word_counts.json` and `database/processed_log.json`.

### 3. View Results
To see the top ranked words by frequency, run the viewer script:
```bash
python view_results.py
```
* This will display the **Top 100** Nouns, Verbs, and Adjectives.

## Configuration (Ignoring Words)

You can customize which words are ignored by editing the `IGNORE_LIST` in `main.py`.

The current configuration includes:
* **Grammar:** Pronouns, prepositions (he, she, in, at, that...).
* **Intensifiers:** Words like *very, really, quite*.
* **Level 1 Verbs:** Functional verbs (be, have, do, will, can).
* **Level 2 Verbs:** Basic vocabulary (go, get, say, make). *Comment this out in the code if you want to include them.*

## Project Structure

```text
WordFreqProject/
├── Input_texts/         # put your .txt files here (Ignored by Git)
├── database/            # stores the JSON results (Ignored by Git)
│   ├── word_counts.json
│   └── processed_log.json
├── main.py              # The core analysis engine
├── view_results.py      # Script to view top lists
└── README.md            # Project documentation
```

## Logic Details

**Why "Quickly" = "Quick"?**
For vocabulary analysis, knowing that a student uses the concept of "quickness" is more important than the specific grammatical form. By converting adverbs to adjectives, we get a truer representation of the lexical range used in the text.

**Why exclude "Be" verbs?**
Verbs like "is/are/was/were" appear in almost every sentence. Including them skews the frequency data and hides the more descriptive verbs (like *analyze, construct, interpret*) that we actually want to find.