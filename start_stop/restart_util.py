import logging
import subprocess
import os
import time
from marqo import Client
import pprint
import json

def rerun_marqo_with_env_vars(env_vars: list = []):
    """
        Given a list of env vars, stop and rerun Marqo using the start script appropriate
        for the current test config

        Returns the console output of all the subprocess calls
    """
    output_1 = "killed marqo or smth"
    run_process = subprocess.Popen([
        "bash",                         # command: run
        "run_marqo_2.sh",               # script to run
        "marqo_docker_0",               # arg $1 in script                           
        ] + env_vars,                   # args $2 onwards
    stdout=subprocess.PIPE, 
    stderr=subprocess.STDOUT, 
    universal_newlines=True)
    
    # Read and print the output line by line (in real time)
    for line in run_process.stdout:
        print(line, end='')
    
    # Wait for the process to complete
    run_process.wait()
    return f"{output_1}\n{run_process.stdout}"

def test_run():
    # Rerun marqo with new custom model
    open_clip_model_object = {
        "model": "open-clip-1",
        "model_properties": {
            "name": "ViT-B-32-quickgelu",
            "dimensions": 512,
            "type": "open_clip",
            "url": "https://github.com/mlfoundations/open_clip/releases/download/v0.2-weights/vit_b_32-quickgelu-laion400m_avg-8a00ab3c.pt"
        }
    }

    print(f"Attempting to rerun marqo with custom model {open_clip_model_object['model']}")
    #rerun_marqo_with_env_vars(
    #    env_vars = f"-e MARQO_MODELS_TO_PRELOAD=[{json.dumps(open_clip_model_object)}]"
    #)
    output = rerun_marqo_with_env_vars(
        env_vars = [
            '-e', f"MARQO_MODELS_TO_PRELOAD=[{json.dumps(open_clip_model_object)}]",
            '-e', f"MARQO_MAX_NUMBER_OF_REPLICAS=5"
        ]
    )
    # print(output)


    # check preloaded models (should be custom model)
    custom_models = ["open-clip-1"]
    res = self.client.get_loaded_models()
    assert set([item["model_name"] for item in res["models"]]) == set(custom_models)

test_run()