# Use this for testing new releases and tags
import random, requests, marqo
import numpy as np
import os
vocab_source = "https://www.mit.edu/~ecprice/wordlist.10000"

# default settings
mq = marqo.Client(
    url=os.environ["MARQO_ENDPOINT_URL"], 
    api_key=os.environ["MARQO_API_KEY"]
)

vocab = requests.get(vocab_source).text.splitlines()

def random_query():
    return " ".join(random.choices(population=vocab, k=10)) 

index_name = "marqo-simplewiki-demo-all"

mq.index(index_name).get_stats()
# {'numberOfDocuments': 112859}

print('MARQO INFO')
# Outputs {'message': 'Welcome to Marqo', 'version': '0.0.19'}
print(mq.get_marqo())

# Testing across limited fields 
number_of_runs = 1000
index_name = "marqo-simplewiki-demo-all"
results = [ mq.index(index_name).search(random_query(), searchable_attributes=["content"], attributes_to_retrieve=["title", "url"] )['processingTimeMs'] for _ in range(number_of_runs)]

print("mean,", sum (results) / len(results))
print("p99,", np.percentile(results, 99))
print("p90,", np.percentile(results, 90))
print("p50,", np.percentile(results, 50))