import marqo
import pprint

mq = marqo.Client(url='http://localhost:8882')

index_settings = {
    "index_defaults": {
        "model": "random",
    }
}

try:
    mq.create_index("throttling-index", settings_dict=index_settings)
except:
    pass

res = mq.index("throttling-index").add_documents(
    [{"_id": str(i), "title": "garbage"} for i in range(1000)]
)

# Not throttled
if "check_test_data" in res:
    print(res["check_test_data"])