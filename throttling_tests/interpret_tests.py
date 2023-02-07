import os
import json


def output_test_desc
# Go through each file in test_data
for filename in os.scandir("test_data"):
    if filename.is_file():
        with open(filename.path) as f:
            raw_json = json.load(f)
            
            output_test_desc(raw_json)



# Output important metrics