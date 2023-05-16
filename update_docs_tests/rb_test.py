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

mq = marqo.Client(url='http://localhost:8882')
num_attempts = 0
attempt_limit = 10

dataset_file = "assets/rb_body.json"

# get the data
data = read_json(dataset_file)
print(f"loaded data with {len(data)} entries")

"""
# other dupe is 141917622
# dupe_test = [d for d in data if d["_id"] == "141917262"]
dupe_test = [d for d in data if d["_id"] == "141917622"]
# pprint.pprint(dupe_test)
print(f"Same? {dupe_test[0] == dupe_test[1]}")

id_list = {}
dupes = []
for d in data:
    if d["_id"] in id_list:
        id_list[d["_id"]] += 1
        dupes.append(d)
        data.remove(d)
    else:
        id_list[d["_id"]] = 1

# pprint.pprint(id_list)

# pprint.pprint(sorted([d["_id"] for d in data]))
"""

print(f"final length: {len(data)} entries")

res = mq.index("rb-index").add_documents(
    data,
    client_batch_size=50,
    device="cuda",
    use_existing_tensors=True,
)

res = mq.index("rb-index").delete()

mq.create_index(index_name="rb-index")

# Source is non-tensor field
res = mq.index("rb-index").add_documents(
    data,
    client_batch_size=50,
    device="cuda",
    use_existing_tensors=True,
    non_tensor_fields=["source_image_url", "available_product_codes"]
)

# Tensor Field is back

res = mq.index("rb-index").add_documents(
    data,
    client_batch_size=50,
    device="cuda",
    use_existing_tensors=True,
    non_tensor_fields=["available_product_codes"]
)


print(res)
"""
Error happens with
- available_product_codes: List and the one to remove is source_image_url
- despite treat_urls_as_pointers
- regardless of model used
"""