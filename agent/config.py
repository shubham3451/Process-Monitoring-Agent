import os
import json


def load_config():
    default_config = {
        "endpoint": os.getenv("ENDPOINT", "http://127.0.0.1:8000/api/ingest/"),
        "api_key": os.getenv("API_KEY", "mysecretapikey"),
        "interval": int(os.getenv("INTERVAL", "5")),
        "max_retries": int(os.getenv("MAX_RETRIES", "5")),
    }
 

    if os.path.exists("agentconfig.json"):
        try:
            print("hello2")
            with open("agentconfig.json", "r") as f:
                file_config = json.load(f)
            default_config.update(file_config)
        except Exception:
            print("⚠️ Failed to load config file, using defaults")

    return default_config
