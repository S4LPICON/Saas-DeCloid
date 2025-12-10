import time
import requests
import threading

def start_heartbeat(node_id, backend_url, node_key, interval):
    def loop():
        while True:
            try:
                print("Sending heartbeat to backend...")
                requests.post(
                    backend_url,
                    json={
                        "daemon_version": "1.0",
                        "docker_version": "25.0",
                        # más stats si quieres
                    },
                    headers={"X-Node-Key": node_key},
                    timeout=5
                )
            except Exception as e:
                print("Heartbeat failed:", e)

            time.sleep(interval)

    threading.Thread(target=loop, daemon=True).start()
