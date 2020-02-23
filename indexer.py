from bs4 import BeautifulSoup
import json
import lxml

doc_id = {}

def posting_dict(doc_id: int, tf: float) -> dict:
     return {"doc_id": doc_id, "tf": tf}

def parse_json(path):
    with open(path, "r") as read_file: 
        file = json.load(read_file)
    soup = BeautifulSoup(file["content"], "lxml")

    # single string containing all the text within the html
    file_content = soup.find_all(['p', 'h1', 'h2', 'h3', 'title'], text=True)
    file_content = ' '.join([e.string for e in file_content])
    return file_content


print(parse_json("DEV/aiclub_ics_uci_edu/8ef6d99d9f9264fc84514cdd2e680d35843785310331e1db4bbd06dd2b8eda9b.json"))