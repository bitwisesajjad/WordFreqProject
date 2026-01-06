import json
import os

# path to database
DB_FILE = os.path.join("database", "word_counts.json")

def load_data():
    """loads the database, hopefully without crashing"""
    if not os.path.exists(DB_FILE):
        print(f"Error: can't find database at {DB_FILE}")
        print("run corpus_tool.py first to generate the data")
        return {}
    
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"something went wrong loading JSON: {e}")
        return {}

def get_top_words(data, pos_filter, limit=100):
    """
    filters by POS (e.g., 'VERB') and returns the top 'limit' words
    basically just sorts and slices
    """
    # collect all words of the requested type
    filtered = [
        (info["lemma"], info["count"]) 
        for key, info in data.items() 
        if info["type"] == pos_filter
    ]
    
    # sort by count (highest first)
    filtered.sort(key=lambda x: x[1], reverse=True)
    
    return filtered[:limit]

def main():
    data = load_data()
    if not data:
        return

    total_words = len(data)
    print(f"--- DATABASE REPORT ---")
    print(f"total unique lemmas: {total_words}\n")
    
    # nouns
    print(f"--- TOP 100 NOUNS ---")
    nouns = get_top_words(data, "NOUN", limit=100)
    for i, (word, count) in enumerate(nouns, 1):
        print(f"{i}. {word} ({count})")

    print("\n" + "="*30 + "\n")
    
    # verbs
    print(f"--- TOP 100 VERBS ---")
    verbs = get_top_words(data, "VERB", limit=100)
    for i, (word, count) in enumerate(verbs, 1):
        print(f"{i}. {word} ({count})")
        
    print("\n" + "="*30 + "\n")

    # adjectives
    print(f"--- TOP 100 ADJECTIVES ---")
    adjs = get_top_words(data, "ADJ", limit=100)
    for i, (word, count) in enumerate(adjs, 1):
        print(f"{i}. {word} ({count})")

if __name__ == "__main__":
    main()