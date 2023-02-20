"""
Throughput and latency test
1 argument: number of docs

Do first:
1. Restart EC2 instance
2. Ensure no docker containers are running
"""

import marqo
import pprint
import time
import sys
import pandas as pd

mq = marqo.Client(url='http://localhost:8882')
colors = ["red", "orange", "green", "blue", "purple"]
fruits = ["apple", "banana", "cherry", "durian", "eggplant"]
names = ["anne", "brian", "charles", "david", "erick"]

# Record machine details in test
print("Update Docs Test")
print("Machine: My Machine")

num_docs = int(sys.argv[1])
client_batch_size = 100
docs = [
    {
        "_id": str(i),
        "color": colors[i % 5],
        "fruit-tensor": fruits[i % 5],
        "name-tensor": names[i % 5],
    }
    for i in range(num_docs)
]


try:
    mq.create_index("update-index", model='onnx/all_datasets_v4_MiniLM-L6')
except:
    pass


# Make sure all fields are non-tensorised
# Set refresh to False
# Client batched
t0 = time.time()
res = mq.index("update-index").add_documents(
    docs,
    non_tensor_fields=["color"],
    client_batch_size=client_batch_size,
    auto_refresh=False,
    device="cpu",
    use_existing_tensors=True
)

# Record time taken for updating + how many. 
batch_results = []
for batch_raw_result in res:
    
    batch_results.append({
        "total_time": batch_raw_result["processingTimeMs"],
        "time_per_doc": batch_raw_result["processingTimeMs"] / client_batch_size
    })

# Interpret the results with pandas
raw_df = pd.DataFrame(batch_results)
print("=" * 30)
print(f"Test: UPDATE DOCS. Number of docs: {num_docs}. Batch size: {client_batch_size}.")
print(f"Summary for time per doc update [in ms]")
pprint.pprint(raw_df["time_per_doc"].describe(percentiles=[.25, .5, .75, .9]))
print("=" * 30)
print(f"Summary for total batch time (batches of {client_batch_size} docs) [in ms]")
pprint.pprint(raw_df["total_time"].describe(percentiles=[.25, .5, .75, .9]))

t1 = time.time()
print(f"Test total time taken: {(t1-t0):.3f}s")