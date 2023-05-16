export MY_MODEL_LIST='[
    "hf/all_datasets_v4_MiniLM-L6",
    {
        "model": "generic-clip-test-model-1",
        "model_properties": {
            "name": "ViT-B-32-quickgelu",
            "dimensions": 512,
            "url": "https://github.com/mlfoundations/open_clip/releases/download/v0.2-weights/vit_b_32-quickgelu-laion400m_avg-8a00ab3c.pt",
            "type": "open_clip"
        }
    }
]'

docker rm marqo
docker run --name marqo --privileged -p 8882:8882 --add-host host.docker.internal:host-gateway \
    -e MARQO_MODELS_TO_PRELOAD="$MY_MODEL_LIST" \
    marqoai/marqo:test