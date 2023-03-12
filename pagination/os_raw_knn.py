import datetime
import functools
import json
import pprint
import time
from typing import Tuple
import numpy as np
from itertools import zip_longest
import utils
import requests
import logging
import urllib3
import math
from typing import (
    List, Optional, Union, Callable, Iterable, Sequence, Dict, Tuple
)

urllib3.disable_warnings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("os_knn_test")
logger.setLevel(logging.DEBUG)

VECTOR_LENGTH = 384
NESTED_OBJECT_NAME = "nested_object"
NESTED_TEXT_FIELD = "some_text_field"
NESTED_VECTOR = "cool_vector_field"

ADMIN_ENDPOINT = 'https://admin:admin@localhost:9200/'
INDEX_NAME = "os_knn_index"

def activate_file_logging():
    """activates logging """
    file_name_date = datetime.datetime.now().strftime("%Y-%m-%d--%H-%M")
    formatter = logging.Formatter(
        "{asctime} {levelname} {message}", style='{')

    fh = logging.FileHandler(f'logs/os_knn_test--{file_name_date}.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def dicts_to_jsonl(dicts: List[dict]) -> str:
    """Turns a list of dicts into a JSONL string"""
    return functools.reduce(
        lambda x, y: "{}\n{}".format(x, json.dumps(y)),
        dicts, ""
    ) + "\n"


def batch_ingest(batch_size: int, total_docs: int, vectors):
    """Generates docs and indexes them with their vectors in
    batches of batch_size. Currently, there is one vector per doc."""
    dataset_t0 = datetime.datetime.now()

    for batch_num in range(total_docs//batch_size):
        batch_t0 = datetime.datetime.now()

        batch_body = []
        for i in range(batch_size):
            doc_num = (batch_num * batch_size) + i
            # ID is auto-generated

            batch_body.append({"index": {"_index": INDEX_NAME, "_id": doc_num}})
            batch_body.append(
            {
                "non_nested_text": f"This doc is number {doc_num}",
                NESTED_OBJECT_NAME: {
                    NESTED_TEXT_FIELD: f"This is nested text for doc number {doc_num}",
                    NESTED_VECTOR: list(vectors[doc_num])
                }
            })
        bulk_index_res = requests.post(
            url=ADMIN_ENDPOINT + INDEX_NAME + "/_bulk",
            data=dicts_to_jsonl(batch_body),
            headers={"Content-Type": "application/json"},
            verify=False
        )
        logger.info(f"Finished indexing batch {batch_num}. Number of docs: {batch_size}, "
                    f"taking {datetime.datetime.now() - batch_t0}. "
                    f"Time per doc: {(datetime.datetime.now() - batch_t0)/batch_size}")
        logger.info(f"    Indexing response: {bulk_index_res.json()}")
    logger.info(f"Finished indexing all batches. Time taken: {datetime.datetime.now() - dataset_t0}")


def create_index(num_shards=1):
    """Creates a kNN index, with a nested vector. """
    vector_index_settings = {
        "settings": {
            "index": {
                "knn": True,
                "knn.algo_param.ef_search": 100,
                "refresh_interval": "30s"
            },
            "number_of_shards": num_shards
        },
        "mappings": {
            "properties": {
                NESTED_OBJECT_NAME: {
                    "type": "nested",
                    "properties": {
                        NESTED_TEXT_FIELD: {
                            "type": "text"
                        },
                        NESTED_VECTOR: {
                            "type": "knn_vector",
                            "dimension": VECTOR_LENGTH,
                            "method": {
                                "name": "hnsw",
                                "space_type": "innerproduct",
                                "engine": "nmslib",
                                "parameters": {
                                    "ef_construction": 128,
                                    "m": 24
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    vector_index_settings_res = requests.put(
        url=ADMIN_ENDPOINT + INDEX_NAME,
        data=json.dumps(vector_index_settings),
        headers={"Content-Type": "application/json"},
        verify=False
    )
    logger.info("Created index. Response: ")
    logger.info(f"    {vector_index_settings_res.json()}")
    logger.info(f"num shards: {num_shards}")


def populate_index(number_docs, batch_size, shard_count):
    """Deletes and recreates the index. Then, populates the index with a generated
    number of docs. The indexing is done in batches of batch_size"""
    vecs_per_doc = 1
    v = np.random.uniform(-1, 1, (number_docs * vecs_per_doc, VECTOR_LENGTH))

    delete_res = requests.delete(
        url=ADMIN_ENDPOINT + INDEX_NAME,
        verify=False
    )
    logger.info(f"Deleted index. Response: ")
    logger.info(f"    {delete_res.json()}")

    create_index(num_shards=shard_count)
    batch_ingest(batch_size=batch_size, total_docs=number_docs, vectors=v)
    log_index_info()


def log_index_info():
    """Logs interesting index info (useful for getting data size)"""
    index_count_res = requests.get(
        url=ADMIN_ENDPOINT + INDEX_NAME + "/_count",
        verify=False
    )
    logger.info(f"Count index. Response: {index_count_res.json()}")

    cat_indices_res = requests.get(
        url=ADMIN_ENDPOINT + "_cat/indices?format=json",
        verify=False
    )
    logger.info(f"cat indices. Response:"
                f"\n{pprint.pformat([stats for stats in cat_indices_res.json() if stats['index'] == INDEX_NAME][0])}")


def search_index(vec, limit, offset) -> None:
    """Searches the index using nested search. Outputs results to log"""
    search_query = {
        "size": limit,
        "from": offset,
        "query": {
            "nested": {
                "path": NESTED_OBJECT_NAME,
                "inner_hits": {},
                "query": {
                    "knn": {
                        f"{NESTED_OBJECT_NAME}.{NESTED_VECTOR}": {
                            "vector": list(vec),
                            "k": limit + offset
                        }
                    }
                },
                "score_mode": "max"
            }
        },
    }
    body = [{"index": INDEX_NAME}, search_query]
    #print("DEBUG BODY")
    #pprint.pprint(body)
    #print(f"Debug type: {type(body[1]['query']['nested']['query']['knn'][f'{NESTED_OBJECT_NAME}.{NESTED_VECTOR}']['vector'][0])}")
    #print(f"Debug content: {body[1]['query']['nested']['query']['knn'][f'{NESTED_OBJECT_NAME}.{NESTED_VECTOR}']['vector'][0]}")
    search_res = requests.get(
        url=ADMIN_ENDPOINT + "/_msearch",
        data=dicts_to_jsonl(body),
        headers={"Content-Type": "application/json"},
        verify=False
    )
    
    assert len(search_res.json()["responses"]) == 1
    query_res = search_res.json()["responses"][0]

    #logger.info(f"Search res. Top hit (ID={query_res['hits']['hits'][0]['_id']}): "
    #            f"{pprint.pformat(query_res['hits']['hits'][0]['_source'][NESTED_OBJECT_NAME][NESTED_TEXT_FIELD])}")
    
    #print("DEBUG: query response")
    #pprint.pprint(query_res["hits"])
    return query_res["hits"]

def refresh_index():
    refresh_res = requests.post(
        url=ADMIN_ENDPOINT + INDEX_NAME + "/_refresh",
        verify=False
    )
    logger.info(f"refreshing index. Response: {pprint.pformat(refresh_res.json())}")


def test_across_parameters(num_queries: int):
    batch_size = 50

    # Tests each combination of all of the following parameters:
    num_list = [100, 200, 1000]
    page_sizes = [1, 10, 100]

    #np.random.seed(2020)
    # queries = np.random.uniform(-1, 1, (num_queries, VECTOR_LENGTH))
    # Generate 1 random query
    queries = np.random.uniform(-1, 1, (1, VECTOR_LENGTH))
    q = queries[0]

    live_updates = True

    # Create index
    # Add raw documents to index
    populate_index(number_docs=max(num_list), batch_size=batch_size, shard_count=5)
    refresh_index()
    time.sleep(5)
    

    results = []

    for num_docs in num_list:

        # DEBUG FULL RESULTS
        t0 = time.time()
        debug_res = search_index(vec=q, limit=num_docs, offset=0)
        debug_res_id_only = [hit["_id"] for hit in debug_res["hits"]]
        t1 = time.time()

        num_docs_result = {"docs_to_search": num_docs, "page_size_results": []}
        for page_size in page_sizes:
            
            page_size_result = {}

            # Execute search
            paginated_search_results = {"hits": []}
            for page_num in range(math.ceil(num_docs / page_size)):
                lim = page_size
                off = page_num * page_size
                
                page_res = search_index(vec=q, limit=lim, offset=off)
                single_page_id_only = [hit["_id"] for hit in page_res["hits"]]
                
                paginated_search_results["hits"].extend(page_res["hits"])
                """
                
                print("========================================================")
                print(f"Query for page num {page_num}")
                print(f"size: {lim}, from: {off}")

                expected_res = debug_res_id_only[off:off+lim]
                print(f"Paginated result for page num  {page_num}: {single_page_id_only}")
                print(f"Expected result for page num  {page_num}: {expected_res}")
                
                if expected_res != single_page_id_only:
                    print("DISCREPANCY FOUND.")
                """

            # Results per page size
            page_id_only = [hit["_id"] for hit in paginated_search_results["hits"]]

            print("========================================================")
            print(f"RESULTS Num Docs: {num_docs}. Page size: {page_size}")
            print(f"NON-PAGINATED RESULTS: (length = {len(debug_res['hits'])})")
            print(debug_res_id_only)

            print(f"PAGINATED: (length = {len(paginated_search_results['hits'])})")
            print(page_id_only)

            page_size_result["page_size"] = page_size
            page_size_result["correctly_paginated"] = debug_res["hits"] == paginated_search_results["hits"]
            page_size_result["num_hits"] = len(debug_res["hits"])

            print("Paginated results same as non-paginated results?")
            print(page_size_result["correctly_paginated"])

            num_docs_result["page_size_results"].append(page_size_result)
        
        results.append(num_docs_result)

    # FINAL RESULT OUTPUT
    pprint.pprint(results)

def test_latency():
    batch_size = 50

    # Tests each combination of all of the following parameters:
    num_list = [10000]
    page_sizes = [100]

    np.random.seed(2020)
    queries = np.random.uniform(-1, 1, (1, VECTOR_LENGTH))
    q = queries[0]

    # Create index
    # Add raw documents to index
    populate_index(number_docs=max(num_list), batch_size=batch_size, shard_count=5)
    refresh_index()
    time.sleep(5)
    

    results = []

    for num_docs in num_list:


        # Get full unpaginated results.
        t0 = time.time()
        debug_res = search_index(vec=q, limit=num_docs, offset=0)
        total_num_hits = len(debug_res["hits"])
        t1 = time.time()

        num_docs_result = {"docs_to_search": num_docs, "page_size_results": [], "query_time": t1-t0}

        # Now we get the same results, but paginated.
        for page_size in page_sizes:
            page_size_result = {"per_page_results": []}

            # Execute search
            for page_num in range(math.ceil(total_num_hits / page_size)):
                per_page_result = {}
                lim = page_size
                off = page_num * page_size
                
                t0 = time.time()
                page_res = search_index(vec=q, limit=lim, offset=off)
                t1 = time.time()

                per_page_result["size"] = lim
                per_page_result["from"] = off
                per_page_result["query_time"] = t1-t0

                page_size_result["per_page_results"].append(per_page_result)

            page_size_result["page_size"] = page_size
            page_size_result["num_hits"] = len(debug_res["hits"])

            num_docs_result["page_size_results"].append(page_size_result)
        
        results.append(num_docs_result)

    # FINAL RESULT OUTPUT
    pprint.pprint(results)



    


# Main code
# test_across_parameters(num_queries=1)
# test_latency()
# log_index_info()