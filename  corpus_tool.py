import spacy
import os
import json
import nltk
import time
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures
from nltk.corpus import stopwords
import string

# config
INPUT_DIR = "Input_texts"
DB_FOLDER = "database"
DB_FILE = os.path.join(DB_FOLDER, "word_counts.json")
LOG_FILE = os.path.join(DB_FOLDER, "processed_log.json")
PHRASE_FILE = os.path.join(DB_FOLDER, "common_phrases.txt")

# make sure db folder exists
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

# quiet download, nobody reads the logs :)
print("checking nltk data...")
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

print("loading spacy...")
# disable the heavy stuff we don't need
nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])

# massive ignore list
# TODO: move this to a text file later so it's not cluttering the code
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
    "important","main","whole","smallest","largest","close","as","great","wide","aware","forth",
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

# --- Helpers ---

def load_json(path):
    # safe load, returns empty dict if fails
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def get_file_metadata(folder):
    """
    Returns dict: {'filename': timestamp}
    Used to detect if a file was edited.
    """
    meta = {}
    if not os.path.exists(folder): return meta
    
    for f in os.listdir(folder):
        if f.endswith(".txt"):
            full_path = os.path.join(folder, f)
            meta[f] = os.path.getmtime(full_path)
    return meta

# --- Core Logic ---

def update_counts(text, db):
    doc = nlp(text)
    for t in doc:
        lemma = t.lemma_.lower()
        pos = t.pos_
        
        if lemma in ignored_words: continue

        # convert adverbs to adjectives logic
        if pos == "ADV":
            pos = "ADJ"
            if lemma.endswith("ily"): lemma = lemma[:-3] + "y"
            elif lemma.endswith("ly"): lemma = lemma[:-2]
            
        if pos in ["NOUN", "VERB", "ADJ"]:
            key = f"{lemma}_{pos}"
            if key in db:
                db[key]["count"] += 1
            else:
                db[key] = {"lemma": lemma, "type": pos, "count": 1}

def run_freq_counter():
    print("\n--- Phase 1: Frequency Counter ---")
    
    db = load_json(DB_FILE)
    old_log = load_json(LOG_FILE)
    
    # migration hack: if old log is a list, wipe it
    if isinstance(old_log, list):
        print("detected legacy log format. resetting history.")
        old_log = {}

    current_files = get_file_metadata(INPUT_DIR)
    if not current_files:
        print(f"no files found in {INPUT_DIR}")
        return

    # diff logic
    to_process = []
    full_rebuild = False

    for fname, mtime in current_files.items():
        if fname not in old_log:
            to_process.append(fname) # new file
        elif old_log[fname] != mtime:
            print(f"File changed: {fname}")
            full_rebuild = True # edited file detected
    
    # if a file was edited, we have to rebuild everything 
    # because subtracting counts is messy and prone to bugs.
    if full_rebuild:
        print("Edited files detected. Rebuilding database from scratch...")
        db = {}
        old_log = {}
        to_process = list(current_files.keys())

    if not to_process:
        print("No changes detected.")
        return

    print(f"Processing {len(to_process)} files...")
    
    for fname in to_process:
        try:
            path = os.path.join(INPUT_DIR, fname)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            update_counts(text, db)
            old_log[fname] = current_files[fname]
            # print(f"done: {fname}")
        except Exception as e:
            print(f"failed to read {fname}: {e}")

    save_json(DB_FILE, db)
    save_json(LOG_FILE, old_log)
    print("Freq DB updated.")

def run_collocations():
    print("\n--- Phase 2: Collocations ---")
    
    # just read everything. 
    # we need the full corpus for stats anyway, can't really do this incrementally.
    tokens = []
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".txt")]
    
    if not files: return

    for fname in files:
        try:
            with open(os.path.join(INPUT_DIR, fname), "r", encoding="utf-8") as f:
                tokens.extend(nltk.word_tokenize(f.read()))
        except:
            pass
            
    if not tokens: return

    bigram_meas = BigramAssocMeasures()
    trigram_meas = TrigramAssocMeasures()
    
    # helper for nltk filter
    stops = set(stopwords.words('english'))
    puncts = set(string.punctuation)
    
    def is_junk(w):
        return w.lower() in stops or w.lower() in ignored_words or w in puncts or len(w) < 3

    # Bigrams
    finder_bi = BigramCollocationFinder.from_words(tokens)
    finder_bi.apply_freq_filter(3)
    finder_bi.apply_word_filter(is_junk)
    top_bi = finder_bi.nbest(bigram_meas.likelihood_ratio, 30)

    # Trigrams
    finder_tri = TrigramCollocationFinder.from_words(tokens)
    finder_tri.apply_freq_filter(3)
    finder_tri.apply_word_filter(is_junk)
    top_tri = finder_tri.nbest(trigram_meas.likelihood_ratio, 20)

    # save
    with open(PHRASE_FILE, "w", encoding="utf-8") as f:
        f.write("--- Bigrams ---\n")
        for p in top_bi: f.write(f"{p[0]} {p[1]}\n")
        f.write("\n--- Trigrams ---\n")
        for t in top_tri: f.write(f"{t[0]} {t[1]} {t[2]}\n")
        
    print(f"Phrases saved to {PHRASE_FILE}")

def main():
    run_freq_counter()
    run_collocations()

if __name__ == "__main__":
    main()