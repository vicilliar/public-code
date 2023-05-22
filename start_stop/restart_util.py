import logging
import subprocess
import os
import time
from marqo import Client
import pprint
import json

def rerun_marqo_with_env_vars(env_vars: str = ""):
    """
        Given a string of env vars, stop and rerun Marqo using the start script appropriate
        for the current test config

        Returns the console output of all the subprocess calls
    """

    run_process = subprocess.Popen([
        "bash",                             # command: run
        "run_marqo_cuda.sh",                # script to run
        "marqo_docker_0",                   # arg $1 in script
        env_vars                            # arg $2 in script
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    
    while True:
        # Read output from pipe in realtime
        output = run_process.stdout.readline()
        
        # Stop if the process is done and there's no more output
        if output == '' and run_process.poll() is not None:
            break

        if output:
            print(output.strip())
    
    run_process.wait()
    print("Marqo restart completed.")

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
    rerun_marqo_with_env_vars(
        env_vars = f"-e MARQO_MODELS_TO_PRELOAD=[]"
    )


    # check preloaded models (should be custom model)
    custom_models = ["open-clip-1"]
    res = self.client.get_loaded_models()
    assert set([item["model_name"] for item in res["models"]]) == set(custom_models)

test_run()