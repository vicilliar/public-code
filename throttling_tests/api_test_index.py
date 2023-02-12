import marqo
import sys
import pprint
import time
import datetime
from marqo.errors import MarqoApiError
import numpy as np
import copy
import math
import json


def read_json(filename: str) -> dict:
    # reads a json file
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def replace_title(data: dict) -> dict:
    # removes the wikipedia from the title for better matching
    data['title'] = data['title'].replace('- Wikipedia', '')
    return data

def split_big_docs(data, field='content', char_len=5e4):
    # there are some large documents which can cause issues for some users
    new_data = []
    for dat in data:
        
        content = dat[field]
        N = len(content)
        
        if N >= char_len:
            n_chunks = math.ceil(N / char_len)
            new_content = np.array_split(list(content), n_chunks)
            
            for _content in new_content:
                new_dat = copy.deepcopy(dat)
                new_dat[field] = ''.join(_content)
                new_data.append(new_dat)
        else:
            new_data.append(dat)
    return new_data

def print_json_status(message):
    now = datetime.datetime.now()
    print('{"timestamp": "' + now.strftime("%Y-%m-%d %H:%M:%S") +'", "process": ' + process_num + ', "message": "' + message + '"}')

def attempt_to_index(docs):
    try:
        print_json_status("starting attempt")
        
        res = mq.index("throttling-index").add_documents(docs, device="cuda", server_batch_size=100)

        print_json_status("success")
        return 0
    
    except Exception as e:
        if e.status_code == 429:
            print_json_status("throttled")
            return -1
        else:
            print_json_status("some other error. reason: " + str(e))
            return -2


process_num = sys.argv[1]
mq = marqo.Client(url='http://localhost:8882')
num_attempts = 0
attempt_limit = 10

"""
Uncomment if you have simplewiki.json
dataset_file = "simplewiki.json"

# get the data
data = read_json(dataset_file)
# clean up the title
data = [replace_title(d) for d in data]
# split big ones to make it easier for users on all hardware
data = split_big_docs(data)
print(f"loaded data with {len(data)} entries")

data = data[:200]
"""

data = [{"_id": str(i), "title": "random values"} for i in range(3000)]
while num_attempts <= attempt_limit:
    res = attempt_to_index(data)
    if res == 0 or res == -2:
        break
    
    # Try again in 30 seconds
    time.sleep(30)
    num_attempts += 1
