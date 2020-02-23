from bs4 import BeautifulSoup
import json

doc_id = {}

def posting_dict(doc_id: int, tf: float) -> dict:
     return {"doc_id": doc_id, "tf": tf}

def parse_json(path):
    file = json.load(path)
    soup = BeautifulSoup(file["content"])

    # single string containing all the text within the html
    file_content = ' '.join([e for e in soup.recursiveChildGenerator()])
    return file_content


print(parse_json("DEV/aiclub_ics_uci_edu/8ef6d99d9f9264fc84514cdd2e680d35843785310331e1db4bbd06dd2b8eda9b.json"))