from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
import math
import json
import numpy
import os
import numpy as np
import time
import linecache

# tracker global variables
porter = PorterStemmer()
words = {}
doc_ids = None

with open("doc_id.txt") as doc_id_txt:
    line = doc_id_txt.readline()
    doc_ids = eval(line)
total_docs = len(doc_ids)

with open("word_number.txt") as w_lines:
    for line in w_lines.readlines():
        terms = line.split()
        words[terms[0]] = int(terms[1])

# # takes in a file path and reads the inverted index 
# def read_inverted(file_path: str):
#     with open(file_path) as index:
#         for line in index.readlines():
#             line = line.rstrip()
#             try:
#                 temp = eval(line)       #everyline has a dictionary
#                 key = list(temp.keys())[0]
#                 value = temp[key]
#                 if key in joined_index:
#                     joined_index[key].extend(value)
#                 else:
#                     joined_index[key] = value
#             except:
#                 print(line)

# os.chdir('indexes')
# for f in os.listdir(os.getcwd()):
#     if os.path.splitext(f)[1] == '.txt' and 'inverted_index' in f:
#         read_inverted(os.path.abspath(f))
# os.chdir('..')

def retrieve_index(word):
    # get inverted_index folder
    letter = word[0]
    if letter not in "abcdefghijklmnopqrstuvwxyz":
        letter = ""
    inverted = linecache.getline("indexes/inverted_index" + letter + ".txt", words[word])
    inverted = eval(inverted)
    key = list(inverted.keys())[0]
    value = inverted[key]
    return key, value

# looks at the "partial" inverted index, returns a list of dictionaries
# if the word exists, else None
# returns up to 10 URLs/Filepaths
def search(term : str) -> list:
    terms = [porter.stem(word) for word in word_tokenize(term.lower())]
    terms, query_vect = mod_query_vector(terms)
    relevant_indexes = {key: value for key, value in [retrieve_index(word) for word in terms]}
    # relevant_indexes = {word: joined_index[word] for word in terms}
    vectors = create_doc_tfidf_matrix(terms, relevant_indexes)
    vectors = get_best_quartile(vectors)
    query_vect = normalize(query_vect)
    vectors = {document: normalize(vectors[document]) for document in vectors}
    cosine_rank = cosine_ranking(query_vect, vectors)
    cos_best = sorted(cosine_rank, key = lambda x: -cosine_rank[x])
    return cos_best[0:10]

def get_best_quartile(vector):
    sum_vector = {doc: sum(vector[doc]) for doc in vector}
    best = sorted(sum_vector, key=lambda x: -sum_vector[x])
    extract = math.floor(len(sum_vector) / 4) if math.floor(len(sum_vector) / 4) >= 10 else len(sum_vector)
    if extract > 1000:
        extract = 1000
    best = best[0:extract + 1]
    return {doc: vector[doc] for doc in best}

def normalize(vector):
    vector = np.array(vector, dtype=float)
    length = np.nansum(vector ** 2) ** 0.5
    vector = vector / length
    return vector

def mod_query_vector(query: list) -> tuple:
    query_set_list = list(set(query))
    q_vect = [0 for _ in query_set_list]
    for term in query:
        if term in query: q_vect[query_set_list.index(term)] += 1
        else: q_vect[query_set_list.index(term)] = 1
    return query_set_list, np.array(q_vect)

# returns a dictionary based on the cosine ranking value, takes in normalized vectors
# NORMALIZE VECTORS BEFORE USING
def cosine_ranking(query_vector: dict, vector: dict):
    return {document: np.nansum(query_vector * vector[document]) for document in vector}

# creates a vectorspace matrix, formatted as to dictionary data structure format
# takes in the terms, and the inverted_indexes. Returns a dictionary with keys as documents,
# and tf-idf as a list. The tf-idf list is later treated as a numpy array object
def create_doc_tfidf_matrix(terms: list, inverted_index: dict) -> dict:
    vector = {} #dictionary - documents are keys, tf-idf expressed as a list initially
    for i in range(len(terms)):
        df = len(inverted_index[terms[i]])
        for document in inverted_index[terms[i]]:
            if document in vector and document in inverted_index[terms[i]]:
                vector[document][i] = calculate_TFIDF(inverted_index[terms[i]][document], df)
            else: 
                vector[document] = [0 for _ in terms]   
                if document in inverted_index[terms[i]]:
                    vector[document][i] = calculate_TFIDF(inverted_index[terms[i]][document], df)
    return vector
    
    
# return the intersection of the documents containing all the terms
def intersect_documents(indexes: list):
    if len(indexes) == 1:
        return indexes
    docu_set = [set(index) for index in indexes]
    docu_intersect = set.intersection(*docu_set)
    intersected = [{docu: tf for docu, tf in index.items() if docu in docu_intersect} for index in indexes]
    return intersected

# merges a list of dictionaries containing a document and a score
def merge_rankings(doc_rankings: dict) -> dict:
    docs = {}
    for doc_dict in doc_rankings:
        for document, ranking in doc_dict.items():
            if document in docs:
                docs[document] += ranking
            else:
                docs[document] = ranking
    return docs

# calculates the tfidf 
def calculate_TFIDF(tf, df) -> float:
    right = tf
    left  = math.log(total_docs / (df + 1)) #ensure not dividng by 0
    return left * right

# changes doc id to url (filepath in this case)
def process_links(links: list) -> list:
    return [doc_ids[link]['url'] for link in links]

# returns actual URL
def get_url(path: str):
    with open("DEV/" + path, "r") as read_file: 
        f = json.load(read_file)
    return f["url"]

searcher = ""
while True:
    searcher = input("INPUT A SEARCH QUERY:\t")
    t1 = time.time()
    if searcher == "get me out of this purgatory": quit()
    try:
        links = search(searcher)
        links = process_links(links)
        t2 = time.time()
        print('\n\tShowing the top', len(links),'results for:', searcher)
        for link in links:
            print('\t', get_url(link))
        print(t2 - t1)
    except:
        print('\tNO RESULTS FOR THE QUERY')
    print('\n')