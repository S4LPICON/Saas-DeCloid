import os
import json
import time
import redis
from src.builder.image_builder import process_task

# ----------------------------
# Configuración de Redis
# ----------------------------
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

# ----------------------------
# Crear tarea de prueba
# ----------------------------
task_id = "test_full_flow"
task = {
    "id": task_id,
    "zip_path": "/home/pinzon/zofrenic-solutions/DeCloidMC/tests_files/server.zip",
    "plugin_path": "/home/pinzon/zofrenic-solutions/DeCloidMC/tests_files/server.jar"
}

# Enviar tarea a Redis
r.lpush("build_tasks", json.dumps(task))
print(f"Tarea creada en Redis: {task_id}")

# ----------------------------
# Worker simulado: procesa la tarea
# ----------------------------
print("Esperando tarea en Redis...")
while True:
    task_str = r.brpop("build_tasks", timeout=5)
    if task_str:
        _, task_json = task_str
        task_data = json.loads(task_json)
        if task_data["id"] == task_id:
            print("Procesando tarea con worker simulado...")
            success, output = process_task(task_data)
            # Guardar resultado en Redis
            r.lpush("build_results", json.dumps({
                "task_id": task_id,
                "success": success,
                "output": output
            }))
            print("Resultado guardado en Redis")
            break
    else:
        print("Esperando...")

# ----------------------------
# Mostrar resultado final
# ----------------------------
result_str = r.lrange("build_results", 0, -1)[0]
result = json.loads(result_str)
print("\n✅ Resultado final de la tarea:")
print(f"Tarea: {result['task_id']}")
print(f"Éxito: {result['success']}")
print(f"Output: {result['output']}")
