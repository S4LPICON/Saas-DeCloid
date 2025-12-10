#!/usr/bin/env python3
#!/usr/bin/env python3
import json
import os
import sys
import shutil
import requests
import docker
import traceback
from datetime import datetime, timezone
import time
from dotenv import load_dotenv


# ─────────────────────────────────────────────
#  LOAD ENV
# ─────────────────────────────────────────────
load_dotenv()
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from src.builder.image_builder import process_task   # -> este archivo que ajustamos abajo


# ─────────────────────────────────────────────
#  WORKER CONFIG
# ─────────────────────────────────────────────
BACKEND_REPORT_URL = os.getenv("BACKEND_REPORT_URL", "").strip()
REQUEST_TIMEOUT = int(os.getenv("BACKEND_REQUEST_TIMEOUT_SEC", "20"))
MAX_RETRIES = int(os.getenv("BACKEND_MAX_RETRIES", "3"))
BACKOFF = float(os.getenv("BACKEND_RETRY_BACKOFF_BASE", "1.8"))


def send_report(task_id: str, task_token: str, payload: dict):
    """
    Envía POST al backend usando Bearer Token + reintentos exponenciales.
    """

    if not BACKEND_REPORT_URL:
        print("❌ BACKEND_REPORT_URL no está configurado")
        return

    url = BACKEND_REPORT_URL.format(task_id=task_id)

    headers = {
        "Authorization": f"Bearer {task_token}",
        "Content-Type": "application/json",
        "User-Agent": "artifacts-worker/1.0"
    }

    attempt = 0
    while attempt <= MAX_RETRIES:
        try:
            attempt += 1
            print(f"[REPORT] Intento {attempt} → POST {url}")

            resp = requests.post(url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)

            if 200 <= resp.status_code < 300:
                print(f"🟢 Reporte enviado OK ({resp.status_code})")
                return

            if 400 <= resp.status_code < 500:
                print(f"🔴 Error permanente {resp.status_code}: {resp.text}")
                return

            print(f"⚠ Error {resp.status_code}, reintentando...")

        except Exception as e:
            print(f"⚠ Error enviando reporte: {e}")

        sleep_time = BACKOFF ** attempt
        print(f"   ⏳ Esperando {sleep_time:.2f}s antes de reintentar…")
        time.sleep(sleep_time)

    print("❌ No se pudo reportar después de múltiples intentos.")


def main():
    if len(sys.argv) < 2:
        print("Se requiere argumento JSON")
        sys.exit(1)

    task = json.loads(sys.argv[1])

    task_id = task["task_id"]
    task_token = task["token"]

    print(f"[WORKER] Procesando task {task_id}")

    success, output = process_task(task)

    if success:
        payload = {
            "success": True,
            "status": "success",
            "version": output.get("version"),
            "size_in_mb": output.get("size_mb"),
            "registry_path": output.get("registry_path"),
            "logs": output.get("logs"),
            "hash_value": output.get("hash"),
            "update_date": datetime.now(timezone.utc).isoformat(),
            "build_id": task.get("build_id"),
        }
    else:
        payload = {
            "success": False,
            "status": "failed",
            "logs": output,
            "update_date": datetime.now(timezone.utc).isoformat(),
            "build_id": task.get("build_id"),
        }

    send_report(task_id, task_token, payload)


if __name__ == "__main__":
    main()
