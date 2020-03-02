from nltk.stem.porter import *
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup
import re
import json
import lxml
import os

doc_id = []
inverted_index = {}
porter = PorterStemmer()

# returns a list of tf's for each word in the document
def process_words(document: str) -> dict:
    document = word_tokenize(document.lower())
    stemmed_words = [porter.stem(word) for word in document]
    num_words = len(stemmed_words)
    tf = {}
    for word in stemmed_words:
        if word in tf: tf[word] += 1 
        else: tf[word] = 1
    for word in tf: tf[word] = tf[word] / num_words
    return tf

def parse_json(path):
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
    return file_content

def process_directory(domain: str):
    os.chdir(os.getcwd() + "/" + domain)
    for site in os.listdir(os.getcwd()):
        current_id = len(doc_id)
        doc_id.append({'id': current_id, 'url': site})
        words_file = parse_json(site)
        tf_dict = process_words(words_file)
        process_tf_dict(tf_dict, current_id)
    os.chdir('..')

def process_tf_dict(tf: dict, doc_id: int):
    for word in tf:
        if word in inverted_index: inverted_index[word].append(posting_dict(doc_id, tf[word]))
        else: inverted_index[word] = [posting_dict(doc_id, tf[word])]

def posting_dict(doc_id: int, tf: float) -> dict:
    return {"id": doc_id, "tf": tf}

def process_dev():
    os.chdir("/Users/kingsleyszeto/Documents/GitHub/cs121-ast3/DEV")
    for f in os.listdir(os.getcwd()):
        if os.path.isdir(f): process_directory(f)

def clean_print():
    for word in inverted_index:
        print(word)
        for posting in inverted_index[word]:
            print('\t', end = "")
            print(posting)

process_dev()
os.chdir('..')
with open("doc_id.txt", "w") as f:
    f.write(str(doc_id))

with open("inverted_index.txt", "w") as f:
    for index in inverted_index:
        temp = {}
        temp[index] = inverted_index[index]
        print(str(temp), file=f)