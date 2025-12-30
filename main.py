'''
This is a script that gets the frequency of verbs, nounds and adjectives fro the input text.

'''

import spacy
import os
import json
from collections import Counter

print ("Hang tight while the NLP model is loaded ...")
nlp = spacy.load ("en_core_web_sm", disable = ["ner", "parser"])

# the folder containing the input texts
INPUT_FOLDER = "Input_texts"
DB_FILE = os.path.join ("database", "word_counts.json")
LOG_FILE= os.path.join ("database", "processed_log.json") # keeping a history of the files already processed.
# the white list of POS that we want to keep
ALLOWED_TAGS = {"NOUN","VERB","ADJ"}
IGNORE_LIST = {
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
"deep","shallow","far","near"
               }
def load_database ():
    if not os.path.exists (DB_FILE):
        return {}
    try:
        with open (DB_FILE, 'r', encoding = "utf-8") as f:
            return json.load (f)
    except json.JSONDecodeError:
        return {}

def save_database (data):
    """
    saves the dictionary to the json file again

    """
    with open (DB_FILE, "w", encoding = "utf-8") as f:
        json.dump (data, f, indent = 5)
def load_log():
    if os.path.exists(LOG_FILE):
        with open (LOG_FILE, "r", encoding = "utf-8") as f:
            return set (json.load(f))
    return set ()
def save_log (log_set):
    with open (LOG_FILE, "w", encoding= "utf-8") as f:
        json.dump(list(log_set), f, indent =5)

def process_text (text, current_db):
    """
    runs the NLP piprline on the text and updates the current_db
    
    :param text: Description
    :param current_db: Description
    """
    doc = nlp (text)
    for token in doc:
        lemma = token.lemma_.lower()
        pos = token.pos_
        if lemma in IGNORE_LIST:
            continue
        if pos=="ADV":
            pos= "ADJ"
            if lemma.endswith ("ily"):
                lemma = lemma [:-3]+ "y" # happily => happy
            elif lemma.endswith ("ly"):
                lemma = lemma [:-2] # quickly => quick

        if pos not in ALLOWED_TAGS:
            continue

        unique_key = f"{lemma}_{pos}"

        if unique_key in current_db:
            current_db [unique_key]["count"]+=1
        else:
            current_db [unique_key] = {
                "lemma": lemma,
                "type": pos,
                "count" : 1
            }

def main ():
    db = load_database ()
    processed_files = load_log()
    print ("__________________________________________")
    print (f"Databse loaded. the number of current unique words: {len(db)}")

    if not os.path.exists (INPUT_FOLDER):
        print ("Error! The folder {INPUT_FOLDER} doesn't exist!")
        return
    all_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".txt")]
    new_files = [f for f in all_files if f not in processed_files]
    if not new_files:
        print (f"No NEW text files found in '{INPUT_FOLDER}'. All the texts are already processed!")
        return
    print ("__________________________________________")
    print (f"Found {len(new_files)} new files. Now processing ...")
    for filename in new_files:
        file_path = os.path.join (INPUT_FOLDER, filename)
        try:
            with open (file_path, "r", encoding = "utf-8") as f:
                text =f.read()
            
            process_text (text,db)
            processed_files.add (filename)

            print (f" -> processed: {filename}")

        except Exception as e:
            print (f"-> Error reading {filename}: {e}")
    save_database (db)
    save_log (processed_files)
    print ("__________________________________________")
    print ("Processing is done now. Database updated!")

if __name__ == "__main__" :
    main ()