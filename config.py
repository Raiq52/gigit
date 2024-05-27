import json
import os
import sys

CONFIG_FILE = "gigit_config.json"

def save_config(backend_repo_path, frontend_repo_path):
    config = {
        "backend_repo_path": backend_repo_path,
        "frontend_repo_path": frontend_repo_path
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Configuration file {CONFIG_FILE} not found. Please run 'gigit init' to set up the repository paths.")
        sys.exit(1)
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    return config["backend_repo_path"], config["frontend_repo_path"]
