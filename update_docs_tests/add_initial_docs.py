# Create initial docs

import marqo
import pprint
import time
import sys

mq = marqo.Client(url='http://localhost:8882')

# Get the same IDs
num_docs = int(sys.argv[1])
docs = [
    {
        "_id": str(i),
        "initial_field": str(i)
    }
    for i in range(num_docs)
]

try:
    mq.create_index("update-index", model='onnx/all_datasets_v4_MiniLM-L6')
except:
    pass

t0 = time.time()
res = mq.index("update-index").add_documents(
    docs,
    non_tensor_fields=["initial_field"],
    client_batch_size=50,
    device="cpu"
)