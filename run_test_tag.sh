export MY_MODEL_LIST='[
    "hf/all_datasets_v4_MiniLM-L6",
    {
        "model": "generic-clip-test-model-2",
        "model_properties": {
            "name": "ViT-B/32",
            "dimensions": 512,
            "type": "clip",
            "url": "https://openaipublic.azureedge.net/clip/models/40d365715913c9da98579312b702a82c18be219cc2a73407c4526f58eba950af/ViT-B-32.pt"
        }
    }
]'

docker run --name marqo --privileged -p 8882:8882 --add-host host.docker.internal:host-gateway \
    -e MARQO_MODELS_TO_PRELOAD="$MY_MODEL_LIST" \
    marqoai/marqo:test