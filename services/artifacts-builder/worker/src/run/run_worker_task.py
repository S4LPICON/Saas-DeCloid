#!/usr/bin/env python3
from datetime import datetime, timezone
import sys
import json
import time
import requests
import os

from dotenv import load_dotenv

load_dotenv()
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from src.builder.image_builder import process_task


BACKEND_REPORT_URL = os.getenv("BACKEND_REPORT_URL", "").strip()
REQUEST_TIMEOUT = int(os.getenv("BACKEND_REQUEST_TIMEOUT_SEC", "20"))
MAX_RETRIES = int(os.getenv("BACKEND_MAX_RETRIES", "3"))
BACKOFF = float(os.getenv("BACKEND_RETRY_BACKOFF_BASE", "1.8"))
print("SIQUIERA ESTOS MENSAJES APARECEN")


def send_report(task_id: str, task_token: str, payload: dict):
    """
    Envía POST al backend usando X-TASK-TOKEN y reintentos exponenciales.
    """
    if not BACKEND_REPORT_URL:
        print("❌ BACKEND_REPORT_URL no está configurado")
        return

    url = BACKEND_REPORT_URL.format(task_id=task_id)
    
    print("task_token=", task_token)
    print("task_id=", task_id)

    
    headers = {
        "Authorization": f"Bearer {task_token}",
        "Content-Type": "application/json",
        "User-Agent": "artifacts-worker/1.0"
    }

    attempt = 0
    while attempt <= MAX_RETRIES:
        try:
            attempt += 1
            print(f"[Report Attempt {attempt}] POST → {url}")

            resp = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )

            # Éxito
            if 200 <= resp.status_code < 300:
                print(f"🟢 Reporte enviado OK ({resp.status_code})")
                return

            # Error del cliente → no reintentar
            if 400 <= resp.status_code < 500:
                print(f"🔴 Error permanente {resp.status_code}: {resp.text}")
                return

            print(f"⚠ Reporte rechazado {resp.status_code}, reintentando...")

        except Exception as e:
            print(f"⚠ Error reportando: {e}")

        # Backoff exponencial
        sleep_time = BACKOFF ** attempt
        print(f"   ⏳ Esperando {sleep_time:.2f}s antes de reintentar...")
        time.sleep(sleep_time)

    print("❌ No se pudo reportar resultado después de múltiples intentos.")


def main():
    if len(sys.argv) < 2:
        print("Se requiere argumento JSON")
        sys.exit(1)

    task = json.loads(sys.argv[1])
    task_id = task["task_id"]
    task_token = task["token"]

    # Ejecutar la build
    success, output = process_task(task)

    if success:
        payload = {
            "success": True,
            "status": "ready",  # ✅ valor correcto
            "version": output.get("version"),
            "size_in_mb": output.get("size_mb"),
            "registry_path": output.get("registry_path"),
            "logs": output.get("logs", output),
            "hash_value": output.get("hash"),
            "update_date": datetime.now(timezone.utc).isoformat()
        }
    else:
        payload = {
            "success": False,
            "status": "failed",  # ✅ valor correcto
            "logs": output,
            "update_date": datetime.now(timezone.utc).isoformat()
        }


    # Reportar al backend
    print(f"[WORKER] task_id={task_id}, enviando token={task_token}")
    


    send_report(task_id, task_token, payload)


if __name__ == "__main__":
    main()
