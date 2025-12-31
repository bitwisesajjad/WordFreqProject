import spacy
import os
import json
import nltk
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures
from nltk.corpus import stopwords
import string

#--- CONFIGURATION ---
INPUT_FOLDER = "Input_texts"
DB_FOLDER = "database"
DB_FILE = os.path.join(DB_FOLDER, "word_counts.json")
LOG_FILE = os.path.join(DB_FOLDER, "processed_log.json")
PHRASE_FILE = os.path.join(DB_FOLDER, "common_phrases.txt")

#Ensure NLTK data is ready
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

print("Loading NLP Brain (spaCy)...")
nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])

#IGNORE LIST (Single List)
ignored_words = {
"very","really","quite","too","so","just","only","even","still","almost","nearly","already","yet","again",
"always","often","usually","sometimes","rarely","never","now","then","soon","later","early","late","here",
"there","everywhere","anywhere","somewhere","away","back","out","in","up","down","on","off","together",
"alone","well","badly","quickly","slowly","easily","hard","clearly","simply","exactly","probably","maybe",
"perhaps","surely","certainly","mostly","mainly","especially","finally","suddenly","recently","usually","nearly",
"be","have","do","go","come","get","make","take","give","use","need","want","like","love","hate","know","think",
"say","tell","ask","answer","feel","seem","look","see","watch","hear","listen","find","call","put","keep","leave",
"stay","become","begin","start","finish","end","work","play","live","die","run","walk","sit","stand","open",
"close","eat","drink","sleep","read","write","speak","talk","drive","ride","buy","sell","pay","bring",
"carry","move","hold","show","help","try","learn","teach","understand","remember","forget","break","cut",
"win","lose", "big","small","large","little","tiny","huge","short","long","tall","high","low","new",
"old","young","early","late","easy","hard","simple","difficult","good","bad","great","nice","fine","real",
"true","false","right","wrong","same","different","other","another","first","last","next","old","modern","basic",
"common","usual","normal","strange","weird","strong","weak","heavy","light","hot","cold","warm","cool","dry",
"wet","clean","dirty","full","empty","open","closed","happy","sad","angry","tired","hungry","beautiful",
"ugly","pretty","funny","serious","quiet","loud","fast","slow","ready","free","possible","impossible",
"important","main","whole","smallest","largest",,"close","as","great","wide","aware","forth",
"water","air","fire","earth","tree","plant","leaf","grass","flower","animal","dog","cat","bird","fish",
"house","home","room","door","window","table","chair","bed","floor","ceiling","wall","school","class",
"teacher","student","book","page","paper","pen","pencil","bag","car","bus","train","bike","road",
"street","city","village","country","river","lake","sea","ocean","mountain","hill","valley","island",
"beach","family","mother","father","parent","child","son","daughter","brother","sister","friend","people",
"person","man","woman","boy","girl","baby","body","head","face","hand","arm","leg","foot","eye","ear","mouth",
"nose","time","day","night","morning","evening","week","month","year","time","moment","place","thing","area",
"side","part","name","number","group","kind","example","problem","answer","story","game","music","sound","color",
"light","dark","rain","snow","wind","weather","general","recent","soft","several","cultural","physical","similar",
"20th","past","final","possible","no","yes","at","moreover","therefore","as","great","chinese"
"form","ground","space","sand","meter","rock","soil","line","height","level","result","be",
"action","life","factor","ice","land","sea","river","mountain","society","human","world",
"forest","jungle","desert","season","winter","fall","summer","spring","ward","type","grow",
"flow","remain","exist","increase","decrease","rise","raise","fill","hope","change","wear",
"set","view","most","upper","also","much","more","total","solid","thus","less","enough",
"necessary","however","many","thin","fat","thick","certain","natural","20th","30th","social",
"deep","shallow","far","near","way"
}

# PHASE 1: WORD FREQUENCY (spaCy)
def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {} if "log" not in filepath else []

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def process_text_frequencies(text, current_db):
    doc = nlp(text)
    for token in doc:
        lemma = token.lemma_.lower()
        pos = token.pos_
        
        if lemma in ignored_words: continue
        
        # Logic: Convert Adverbs to Adjectives. We don't need to list adverbs, we cound them as the adj version of them.
        if pos == "ADV":
            pos = "ADJ"
            if lemma.endswith("ily"): lemma = lemma[:-3] + "y"
            elif lemma.endswith("ly"): lemma = lemma[:-2]
            
        if pos not in {"NOUN", "VERB", "ADJ"}: continue
            
        unique_key = f"{lemma}_{pos}"
        if unique_key in current_db:
            current_db[unique_key]["count"] += 1
        else:
            current_db[unique_key] = {"lemma": lemma, "type": pos, "count": 1}

def run_frequency_analysis():
    print("\n--- PHASE 1: Word Frequency Analysis ---")
    db = load_json(DB_FILE)
    processed_log = set(load_json(LOG_FILE))
    
    if not os.path.exists(INPUT_FOLDER):
        print(f"Error: {INPUT_FOLDER} not found.")
        return

    all_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".txt")]
    new_files = [f for f in all_files if f not in processed_log]
    
    if not new_files:
        print("No new files for frequency counting.")
    else:
        print(f"Processing {len(new_files)} new files...")
        for filename in new_files:
            try:
                with open(os.path.join(INPUT_FOLDER, filename), "r", encoding="utf-8") as f:
                    text = f.read()
                process_text_frequencies(text, db)
                processed_log.add(filename)
                print(f" -> Counted: {filename}")
            except Exception as e:
                print(f" -> Error: {filename} : {e}")
        
        save_json(DB_FILE, db)
        save_json(LOG_FILE, list(processed_log))
        print("Database updated.")

#PHASE 2: COLLOCATIONS (NLTK)
def get_all_text_tokens():
    """Reads ALL files to find patterns across the whole corpus."""
    all_tokens = []
    files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".txt")]
    
    for filename in files:
        path = os.path.join(INPUT_FOLDER, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                all_tokens.extend(nltk.word_tokenize(f.read()))
        except:
            pass
    return all_tokens

def run_collocation_analysis():
    print("\n--- PHASE 2: Phrase & Collocation Extraction ---")
    print("Reading full corpus to find patterns...")
    tokens = get_all_text_tokens()
    
    if not tokens:
        print("No text found.")
        return

    bigram_measures = BigramAssocMeasures()
    trigram_measures = TrigramAssocMeasures()
    
    stop_words = set(stopwords.words('english'))
    punctuation = set(string.punctuation)
    
    #I add the 'ignored_words' to the NLTK filter too
    def filter_stops(w):
        return w.lower() in stop_words or w.lower() in ignored_words or w in punctuation or len(w) < 3

    #1.Bigrams
    finder_bi = BigramCollocationFinder.from_words(tokens)
    finder_bi.apply_freq_filter(3)
    finder_bi.apply_word_filter(filter_stops)
    top_bi = finder_bi.nbest(bigram_measures.likelihood_ratio, 30)

    #2. Trigrams
    finder_tri = TrigramCollocationFinder.from_words(tokens)
    finder_tri.apply_freq_filter(3)
    finder_tri.apply_word_filter(filter_stops)
    top_tri = finder_tri.nbest(trigram_measures.likelihood_ratio, 20)

    with open(PHRASE_FILE, "w", encoding="utf-8") as f:
        f.write("--- TOP 30 2-WORD PHRASES (Bigrams) ---\n")
        for pair in top_bi:
            f.write(f"{pair[0]} {pair[1]}\n")
        
        f.write("\n--- TOP 20 3-WORD PHRASES (Trigrams) ---\n")
        for triple in top_tri:
            f.write(f"{triple[0]} {triple[1]} {triple[2]}\n")

    print(f"Success! Common phrases saved to: {PHRASE_FILE}")
    print("\nTop 5 Phrases Found:")
    for i, pair in enumerate(top_bi[:5]):
        print(f" {i+1}. {pair[0]} {pair[1]}")

def main():
    run_frequency_analysis()
    run_collocation_analysis()

if __name__ == "__main__":
    main()