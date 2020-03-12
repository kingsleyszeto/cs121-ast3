from simhash import Simhash, SimhashIndex       #from https://github.com/leonsim/simhash
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup
import re
import json
import lxml
import os
import math
import pprint

LETTERS = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", ""]
doc_id = []
inverted_index = {}
hashed = SimhashIndex([], k=0)
porter = PorterStemmer()

# returns a list of tf's for each word in the document
def process_words(document: str) -> dict:
    document = word_tokenize(document.lower())
    stemmed_words = [porter.stem(word) for word in document]
    tf = {}
    for word in stemmed_words:
        if word in tf: tf[word] += 1 
        else: tf[word] = 1
    for word in tf: tf[word] = math.log(tf[word]) + 1
    return tf

# function that parses a json file and extracts all the words
# returns the document in one large string.
def parse_json(path) -> str:
    with open(path, "r") as read_file: 
        file = json.load(read_file)
    soup = BeautifulSoup(file["content"], "lxml")

    # single string containing all the text within the html
    # file_content = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'a', 'title', 'span'], text=True)
    # file_content = ' '.join([e.string for e in file_content])
    # file_content = ' '.join([e.string for e in soup.recursiveChildGenerator() if isinstance(e, str)])
    for tag in soup.find_all(['script', 'style']):
        tag.extract()
    file_content = soup.get_text(" ")

    # find text within tags with higher weight
    weighted_content = soup.find_all(['h1', 'h2', 'h3', 'b', 'a'], text=True)
    weighted_content = ' '.join([e.string for e in weighted_content])

    return file_content + " " + weighted_content

# process the directory of the dev file
def process_directory(domain: str):
    print(domain)
    os.chdir(os.getcwd() + "/" + domain)

    for site in os.listdir(os.getcwd()):
        current_id = len(doc_id)
        doc_id.append({'id': current_id, 'url': domain + '/' + site})
        words_file = parse_json(site)
        simhashed_words = Simhash(words_file)
        if len(hashed.get_near_dups(simhashed_words)) <= 0:
            hashed.add(site, simhashed_words)
            tf_dict = process_words(words_file)
            process_tf_dict(tf_dict, current_id)
    os.chdir('..')

# takes the tf dict associated with a document_id. Puts all the words of that
# document into the cumulative inverted index
def process_tf_dict(tf: dict, doc_id: int):
    for word in tf:
        if word in inverted_index: inverted_index[word][doc_id] = tf[word]
        else: inverted_index[word] = {doc_id: tf[word]}

# includes only the document id as a key and it's term-frequency
def posting_dict(doc_id: int, tf: float) -> dict:
    return {doc_id: tf}

# processes the entire dev file given to us
def process_dev():
    os.chdir("/Users/bryanly/Documents/UCI Brilliant Future/CS 121/cs121-ast3/DEV")
    # os.chdir("/Users/kingsleyszeto/Documents/GitHub/cs121-ast3/DEV")
    partial_index_count = 1
    for f in os.listdir(os.getcwd()):
        if os.path.isdir(f): process_directory(f)
        if len(inverted_index) > 200000:
            write_partial_index(partial_index_count)
            partial_index_count += 1
    write_partial_index(partial_index_count)

        
# prints the inverted index with clean indentation
def clean_print():
    for word in inverted_index:
        print(word)
        for posting in inverted_index[word]:
            print('\t', end = "")
            print(posting)

# sorts and writes partial index to a file and clears the dictionary
def write_partial_index(partial_index_count: int):
    with open("../indexes/partial_index" + str(partial_index_count) + ".txt", "w") as file:
        file.write(str(inverted_index))
    inverted_index.clear()

def run_partial_index_creation():
    # deletes the contents of indexes/ before running

    temp_partial_index_count = 1
    while(os.path.exists("indexes/partial_index" + str(temp_partial_index_count) + ".txt")):
        os.remove("indexes/partial_index" + str(temp_partial_index_count) + ".txt")
        temp_partial_index_count += 1

    # deletes word_index before running
    if os.path.exists("word_index.txt"):
        os.remove("word_index.txt")

    process_dev()
    os.chdir('..')

    with open("doc_id.txt", "w") as f:
        f.write(str(doc_id))

# merges all the partial indicies into a set of alphabetically organized indices
def merge_index():
    #clear existing inverted index files
    for letter in LETTERS:
        if(os.path.exists("indexes/inverted_index" + letter + ".txt")):
            os.remove("indexes/inverted_index" + letter + ".txt")

    partial_index_list = get_indices()
    for letter in LETTERS:
        print(letter)
        letter_index = make_full_letter_index(letter, partial_index_list)
        with open("indexes/inverted_index" + letter + ".txt", "w") as open_file:
            for word in letter_index:
                print("{\'" + word + "\': " + str(letter_index[word]) + "}", file=open_file)


# makes and index of all words starting with the passed letter
def make_full_letter_index(letter: str, partial_index_list: list):
    letter_index = {}
    for partial_index in partial_index_list:
        print(partial_index)
        letter_index.update(make_partial_letter_index(letter, partial_index))
    return letter_index

# makes an index of all words in the given partial index starting with the passed letter
def make_partial_letter_index(letter: str, partial_index: str):
    partial_letter_index = {}
    with open(partial_index, "r") as file:
        temp_index = eval(file.read())
    
    if letter != "":
        for word in [key for key in temp_index.keys() if key.startswith(letter)]:
            partial_letter_index[word] = temp_index[word]
    else:
        for word in [key for key in temp_index.keys() if key[:1] not in LETTERS]:
            partial_letter_index[word] = temp_index[word]

    return partial_letter_index


# returns a list of the paths to all the partial indices
def get_indices():
    indices = []
    temp_partial_index_count = 1
    while(os.path.exists("indexes/partial_index" + str(temp_partial_index_count) + ".txt")):
        indices.append("indexes/partial_index" + str(temp_partial_index_count) + ".txt")
        temp_partial_index_count += 1
    return indices

# run_partial_index_creation()
# merge_index()