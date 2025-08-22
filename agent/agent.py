import time
import json
import gzip
import base64
from datetime import datetime
from system_info import get_system_info
from config import load_config
from process import collect_process_data
from sender import send_data

def main():
    config = load_config()

    print("🔹 Process Monitoring Agent Started")
    print(f"➡ Endpoint: {config['endpoint']}")
    print(f"➡ Polling interval: {config['interval']}s")
    print("-" * 60)

    while True:
        try:

            process_data = collect_process_data()

            system_info = get_system_info()

            snapshot = {
                "hostdetails": system_info,
                "snapshot_time": datetime.utcnow().isoformat(),
                "processes": process_data
            }

            print(f"[{snapshot['snapshot_time']}] Collected {len(process_data)} processes")


            raw_json = json.dumps(snapshot).encode("utf-8")
            compressed = gzip.compress(raw_json)
            encoded = base64.b64encode(compressed).decode("utf-8")

            success = send_data(encoded, config)

            if success:
                print(" Sending System Info...")
            else:
                print(" Failed to send data")

        except Exception as e:
            print(f" Agent error: {e}")

        time.sleep(config["interval"])

if __name__ == "__main__":
    main()


