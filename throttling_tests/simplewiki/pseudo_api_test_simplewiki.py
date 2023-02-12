import sys
import marqo
import pprint
import os
import subprocess
import json
import time

t0 = time.time()
mq = marqo.Client(url='http://localhost:8882')

def chunk_list(list, chunk_size):
    for i in range(0, len(list), chunk_size):
        yield list[i:i + chunk_size]

def split_json_file(file_name, thread_attempts):
    with open(file_name, 'r') as f:
        data = json.load(f)
    
    chunk_size = len(data) // thread_attempts
    chunked_data = list(chunk_list(data, chunk_size))
    

    for i, chunk in enumerate(chunked_data):
        with open("".join(file_name.split(".")[:-1]) + str(i+1) + ".json", 'w') as f:
            json.dump(chunk, f)

try:
    mq.create_index("throttling-index", model='onnx/all_datasets_v4_MiniLM-L6')
except:
    pass

# chunk json file into 20 files
t0_chunk = time.time()

thread_attempts = sys.argv[1]
file_name = "json_files/simplewiki.json"
split_json_file(file_name, int(thread_attempts)-1)

t1_chunk = time.time()
print(f"JSON splitting time: {(t1_chunk-t0_chunk):.3f}s")


# run subprocess (20 threads or so)
std_output = subprocess.run(['seq 1 ' + str(thread_attempts) + ' | xargs -I% -n1 -P' + str(thread_attempts) \
+ ' python3 api_test_index_simplewiki.py %'], shell=True, stdout=subprocess.PIPE).stdout.decode()

# catch the output (json format).
# reads in the order it got to the terminal
json_list = []
statuses = dict()
for line in std_output.splitlines():
    try:
        json_data = json.loads(line.replace("'", "\""))
        
        if json_data['message'] in statuses:
            statuses[json_data['message']] += 1
        else:
            statuses[json_data['message']] = 1
        
        json_list.append(json_data)
    except json.JSONDecodeError as e:
        print(f"error decoding the json line {line}")
        print(f"reason: {e}")
        # skip lines that are not in JSON format
        continue

print("Full output")
pprint.pprint(sorted(json_list, key=lambda i: i['timestamp']))

print("====================================\n")
print(f"Stats for {thread_attempts} concurrent attempts")
pprint.pprint(statuses)

t1 = time.time()
print(f"Total Time Taken: {(t1-t0):.3f}s")
