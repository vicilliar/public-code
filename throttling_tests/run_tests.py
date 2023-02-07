import os
import subprocess
import json
import marqo
import pprint
import time

mq = marqo.Client(url='http://localhost:8882')

# constants

solution = {
    "o": "sorted sets",
    "s": "regular sets"
}

machine = {
    "c": "pc (16gb ram, 3600, 6 core)",
    "e": "ec2 instance (g4dn.xlarge)"
}

expiry = {
    "i": "immediately expire keys",
    "a": "asynchronously expire keys"
}

thread_counts = {
    "a": {
        "max_threads": 10,
        "thread_attempts": 11
    },
    "b": {
        "max_threads": 20,
        "thread_attempts": 21
    },
    "c": {
        "max_threads": 40,
        "thread_attempts": 41
    },
    "d": {
        "max_threads": 100,
        "thread_attempts": 101
    },
    "e": {
        "max_threads": 1000,
        "thread_attempts": 1001
    },
}


"""
    swap out tests you want to run here
    NOTE BEFORE RUNNING, manually change the o/s and p/w here depending on your branch.
"""

test_codes = ["seia", "seib", "seic", "seid"]

for code in test_codes:
    
    test_data_file = f"test_data/{code}.json"

    # Only run test if its data doesn't exist yet
    if not os.path.exists(test_data_file):
        
        t0 = time.time()
        print(f"RUNNING TEST: {code}")
        # set thread count and attempts
        max_threads = thread_counts[code[3]]["max_threads"]
        mq.set_max_concurrent_index(max_threads)

        thread_attempts = str(thread_counts[code[3]]["thread_attempts"])

        # run the subprocess
        std_output = subprocess.run(['seq 1 ' + str(thread_attempts) + ' | xargs -I% -n1 -P' + str(thread_attempts) + ' python3 test_index.py'], shell=True, stdout=subprocess.PIPE).stdout.decode()
        # for each JSON line of output, append extra data from here (code, desc, max, attempted)

        json_output_list = []

        for line in std_output.splitlines():
            try:
                json_data = json.loads(line.replace("'", "\""))

                json_data["code"] = code
                json_data["desc"] = f"{solution[code[0]]}, {machine[code[1]]}, {expiry[code[2]]}"
                json_data["supposed_max_threads"] = max_threads
                json_data["attempted_threads"] = thread_counts[code[3]]["thread_attempts"]

                json_output_list.append(json_data)
            except json.JSONDecodeError as e:
                print(f"error decoding the json line {line}")
                print(f"reason: {e}")
                # skip lines that are not in JSON format
                continue

        t1 = time.time()
        print(f"Test {code} finished in {(t1-t0):.3f}s.")
        # write json to file
        with open(test_data_file, "w") as f:
            json.dump(json_output_list, f, indent=5)
    
    else:
        print(f"Skipping {test_data_file}, as it has already been run.")
