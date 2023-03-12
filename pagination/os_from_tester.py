import marqo
import pprint
import requests
import random
import math

# Test bug in pagination feature of OpenSearch
# Create marqo index
mq = marqo.Client(url='http://localhost:8882')

try:
    mq.index("my-first-index").delete()
except:
    pass

# Index set number of documents
# 100 random words
vocab_source = "https://www.mit.edu/~ecprice/wordlist.10000"
vocab = requests.get(vocab_source).text.splitlines()
num_docs = 100
random.seed(2020)
docs = [{"Title": "a " + (" ".join(random.choices(population=vocab, k=25))),
                    "_id": str(i)
                    }
                  for i in range(num_docs)]

mq.index("my-first-index").add_documents(
            docs, auto_refresh=False
        )
mq.index("my-first-index").refresh()
search_method = "TENSOR"

# Search for all 100 documents at the same time
# DEBUG FULL RESULTS
debug_res = mq.index("my-first-index").search(
                search_method=search_method,
                q='a', 
                limit=num_docs)
debug_res_id_only = [hit["_id"] for hit in debug_res["hits"]]

# Search for pages of 1 document at a time
for page_size in [1]:
    print("========================================================")
    print(f"{search_method}: Results for page_size = {page_size}")

    paginated_search_results = {"hits": []}
    for page_num in range(math.ceil(num_docs / page_size)):
        lim = page_size
        off = page_num * page_size
        # print(f"Now testing: limit={lim}, offset={off}")
        page_res = mq.index("my-first-index").search(
                        search_method=search_method,
                        q='a', 
                        limit=lim, offset=off)
        single_page_id_only = [hit["_id"] for hit in page_res["hits"]]
        
        paginated_search_results["hits"].extend(page_res["hits"])
        print("========================================================")
        print(f"Query for page num {page_num}")
        print(f"size: {page_res['limit']}, from: {page_res['offset']}")

        expected_res = debug_res_id_only[off:off+lim]
        print(f"Paginated result for page num  {page_num}: {single_page_id_only}")
        print(f"Expected result for page num  {page_num}: {expected_res}")
        
        if expected_res != single_page_id_only:
            print("DISCREPANCY FOUND.")
    
    page_id_only = [hit["_id"] for hit in paginated_search_results["hits"]]
    
    print("========================================================")
    print(f"FULL RESULTS: (length = {len(debug_res['hits'])})")
    print(debug_res_id_only)

    print(f"PAGINATED: (length = {len(paginated_search_results['hits'])})")
    print(page_id_only)

    print("Paginated results same as expected full results?")
    print(debug_res["hits"] == paginated_search_results["hits"])





