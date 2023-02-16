import sys
import marqo
import pprint
import os
import subprocess
import json
import time

t0 = time.time()
mq = marqo.Client(url='http://localhost:8882')
thread_attempts = sys.argv[1]

try:
    mq.create_index("throttling-index", model='onnx/all_datasets_v4_MiniLM-L6')
except:
    pass

# run subprocess (100 threads or so)
std_output = subprocess.run(['seq 1 ' + str(thread_attempts) + ' | xargs -I% -n1 -P' + str(thread_attempts) \
+ ' python3 api_test_index.py %'], shell=True, stdout=subprocess.PIPE).stdout.decode()

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