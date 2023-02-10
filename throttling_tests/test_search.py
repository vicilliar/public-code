import marqo
import pprint

mq = marqo.Client(url='http://localhost:8882')

results = mq.index("throttling-index").search(
    q="", 
    search_method="TENSOR"
)

pprint.pprint(results)