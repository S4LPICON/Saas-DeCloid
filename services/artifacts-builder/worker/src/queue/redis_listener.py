# Archivo: src/queue/redis_listener.py

from dotenv import load_dotenv   # 🔹 Agrega esto al inicio
import os
import json
import redis
from src.builder.image_builder import process_task

# 🔹 Cargar variables desde .env (de la raíz del proyecto)
load_dotenv()

# Configuración de Redis y Registry usando las variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REGISTRY_URL = os.getenv("REGISTRY_URL", "localhost:5000")

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

def listen_for_task():
    print("Worker escuchando tareas en Redis...")
    while True:
        task_entry = redis_client.brpop("build_tasks", timeout=5)
        if task_entry:
            _, task_str = task_entry
            task = json.loads(task_str)
            print(f"Tarea recibida: {task['id']}")
            success, output = process_task(task)
            redis_client.lpush("build_results", json.dumps({
                "task_id": task["id"],
                "success": success,
                "output": output
            }))
            print(f"Tarea {task['id']} procesada. Éxito: {success}")
            print("Output:", output)

if __name__ == "__main__":
    listen_for_task()
