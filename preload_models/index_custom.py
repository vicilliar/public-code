import marqo
mq = marqo.Client()
settings = {
    "index_defaults": {
        "treat_urls_and_pointers_as_images": True,
        "model": 'generic-clip-test-model-1',
        "model_properties": {
            "name": "ViT-B-32-quickgelu",
                "dimensions": 512,
                "url": "https://github.com/mlfoundations/open_clip/releases/download/v0.2-weights/vit_b_32-quickgelu-laion400m_avg-8a00ab3c.pt",
                "type": "open_clip"
            },
        "normalize_embeddings": True,
    },
}
try:
    mq.delete_index("my-own-clip", settings_dict=settings)
except:
    pass

response = mq.create_index("my-own-clip", settings_dict=settings)

mq.index("my-own-clip").add_documents(
    [
        {"_id": "1", "field_1": "hello"}, 
        {"_id": "2", "field_1": "red"}, 
        {"_id": "3", "field_1": "cabbage"}, 
    ]
)
res = mq.index("my-own-clip").search("vegetable")
print("search results are: ")
print(res)