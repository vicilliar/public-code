import marqo
import numpy as np
mq = marqo.Client()

index_settings = {
    "index_defaults": {
        "model": "open_clip/ViT-B-32-quickgelu/laion400m_e31",
        "normalize_embeddings": True
    }
}

index_name = "joshua-index"
try:
    mq.delete_index(index_name)
except:
    pass

mq.create_index(index_name, settings_dict=index_settings)

mq.index(index_name).add_documents([{"_id": "explicit_cpu", "title": "blah"}], device="cpu")
mq.index(index_name).add_documents([{"_id": "explicit_cuda", "title": "blah"}], device="cuda")
mq.index(index_name).add_documents([{"_id": "default_device", "title": "blah"}])

cpu_vec = mq.index(index_name).get_document(document_id="explicit_cpu", expose_facets=True)['_tensor_facets'][0]["_embedding"]
cuda_vec = mq.index(index_name).get_document(document_id="explicit_cuda", expose_facets=True)['_tensor_facets'][0]["_embedding"]
default_vec = mq.index(index_name).get_document(document_id="default_device", expose_facets=True)['_tensor_facets'][0]["_embedding"]

print(f"cpu_vec: {cpu_vec[:5]}")
print(f"cuda_vec: {cuda_vec[:5]}")
print(f"default_vec: {default_vec[:5]}")
print(f"np.abs(a - b).sum() is {np.abs(np.array(cpu_vec) - np.array(cuda_vec)).sum()}")

# Confirm that CUDA was used by default.
assert not np.allclose(np.array(cpu_vec), np.array(default_vec), atol=1e-5)
assert np.allclose(np.array(cuda_vec), np.array(default_vec), atol=1e-5)