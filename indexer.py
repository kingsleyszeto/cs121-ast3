from nltk.stem.porter import *
import re

doc_id = {}
inverted_index = {}
porter = PorterStemmer()

def posting_dict(doc_id: int, tf: float) -> dict:
    return {"doc_id": doc_id, "tf": tf}

# returns a list of tf's for each word in the document
def process_words(document: str) -> dict:
    document = document.replace('\n', '').replace('\t', '')
    num_words = len(document)
    stemmed_words = [porter.stem(re.sub(r'[^A-Za-z0-9]+', '', word)) for word in document]

    tf = {}
    for word in stemmed_words:
        if word in tf: tf[word] += 1 
        else: tf[word] = 1
    for word in tf: tf[word] = tf[word] / num_words
    return tf
