import time
import requests

def send_data(data, config):
    headers = {
        "Authorization": f"ApiKey {config['api_key']}",
        "Content-Type": "application/json"
    }
    url = config["endpoint"]

    backoff = 1
    for attempt in range(config["max_retries"]):
        try:
            response = requests.post(url, json={"payload": data}, headers=headers, timeout=10)
            if response.status_code in (200, 201):
                return True
            else:
                print(f"Server returned {response.status_code}: {response.text}")
        except Exception as e:
            print(f" Send failed: {e}")

        print(f" Retrying in {backoff}s...")
        time.sleep(backoff)
        backoff *= 2 

    return False
