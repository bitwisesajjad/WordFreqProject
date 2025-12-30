import json
import os

# Path to your database
DB_FILE = os.path.join("database", "word_counts.json")

def load_data():
    """Loads the database safely."""
    if not os.path.exists(DB_FILE):
        print(f"Error: Database file not found at {DB_FILE}")
        print("Please run main.py first to generate the data.")
        return {}
    
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return {}

def get_top_words(data, pos_filter, limit=100):
    """
    Filters by POS (e.g., 'VERB') and returns the top 'limit' words.
    """
    # 1. Collect all words of the requested type
    # We create a list of tuples: ("eat", 50)
    filtered = [
        (info["lemma"], info["count"]) 
        for key, info in data.items() 
        if info["type"] == pos_filter
    ]
    
    # 2. Sort by count (Highest first)
    filtered.sort(key=lambda x: x[1], reverse=True)
    
    # 3. Return the top N results
    return filtered[:limit]

def main():
    data = load_data()
    if not data:
        return

    total_words = len(data)
    print(f"--- DATABASE REPORT ---")
    print(f"Total unique lemmas found: {total_words}\n")
    
    # --- NOUNS ---
    print(f"--- TOP 100 NOUNS ---")
    nouns = get_top_words(data, "NOUN", limit=100)
    for i, (word, count) in enumerate(nouns, 1):
        print(f"{i}. {word} ({count})")

    print("\n" + "="*30 + "\n")
    
    # --- VERBS ---
    print(f"--- TOP 100 VERBS ---")
    verbs = get_top_words(data, "VERB", limit=100)
    for i, (word, count) in enumerate(verbs, 1):
        print(f"{i}. {word} ({count})")
        
    print("\n" + "="*30 + "\n")

    # --- ADJECTIVES ---
    print(f"--- TOP 100 ADJECTIVES ---")
    adjs = get_top_words(data, "ADJ", limit=100)
    for i, (word, count) in enumerate(adjs, 1):
        print(f"{i}. {word} ({count})")

if __name__ == "__main__":
    main()