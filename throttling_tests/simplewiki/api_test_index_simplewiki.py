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

def attempt_to_index(docs, batch_size):
    try:
        print_json_status(f"starting attempt")
        print(f"Process {process_num} with {len(docs)} docs left in the queue")
        res = mq.index("throttling-index-2").add_documents(docs[:batch_size])
        docs = docs[batch_size:]
        print_json_status("success")
        return docs
    
    except Exception as e:
        if e.status_code == 429:
            print_json_status("throttled")
        else:
            print_json_status(f"error code: {e.status_code}")
    
    finally:
        return docs

def add_ids(docs_to_index):
    for i in range(len(docs_to_index)):
        docs_to_index[i]['_id'] = str(hash(json.dumps(docs_to_index[i])))
    
    return docs_to_index

process_num = sys.argv[1]
mq = marqo.Client(url='http://localhost:8882')
num_attempts = 1
batch_size = 24
t0 = time.time()

"""
Change these values before running large test
"""
attempt_limit = 5000       # change to 1000
small_sample_size = -1      # change to -1

dataset_file = f"json_files/simplewiki{process_num}.json"

# get the data
data = read_json(dataset_file)
# clean up the title
data = [replace_title(d) for d in data]
# split big ones to make it easier for users on all hardware
data = split_big_docs(data)
data = add_ids(data)

if small_sample_size != -1 and len(data) >= small_sample_size:
    data = data[:small_sample_size]

total_doc_num = len(data)
print(f"Process {process_num} loaded data with {total_doc_num} entries")

while num_attempts <= attempt_limit:
    data = attempt_to_index(data, batch_size)
    if len(data) == 0:
        break
    
    # Try again in 10 seconds
    time.sleep(10)
    num_attempts += 1

t1 = time.time()
time_taken = f"{(t1-t0):.3f}"
now = datetime.date.now()
docs_indexed = total_doc_num - len(data)

# Final results
print('{"process": ' + str(process_num) + ', ' + \
'"message": "summary", ' + \
'"timestamp": "'  + now.strftime("%Y-%m-%d %H:%M:%S") + '", ' + \
'"docs_indexed": "'  +  str(docs_indexed) + '/' + str(total_doc_num) + '", ' + \
'"attempts_made": '  + str(num_attempts) + ', ' + \
'"time taken": "'  + str(time_taken) + '"}' )