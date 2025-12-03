import uuid
import json
import redis
import jwt
from datetime import datetime, timedelta

from decloid.settings.base import SECRET_KEY

redis_pool = redis.ConnectionPool(host="localhost", port=6379, db=0, decode_responses=True)
r = redis.Redis(connection_pool=redis_pool)

def enqueue_build_task(artifact):
    task_id = str(uuid.uuid4())
    payload = {
        "task_id": task_id,
        "artifact_uuid": str(artifact.artifact_uuid),
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    task_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    print("Token JWT:", task_token)

    task = {
        "task_id": task_id,
        "token": task_token,
        "artifact_uuid": str(artifact.artifact_uuid),
        "zip_path": artifact.zip_file.path,
        "plugin_path": "/home/pinzon/zofrenic-solutions/DeCloidMC(only local) OLD/tests_files/worldedit.jar",
    }

    # Enviar a Redis (solo la tarea, ya no necesitas guardar token allí)
    r.lpush("build_tasks", json.dumps(task))

    # Estado inicial
    r.hset(f"build_status:{task_id}", mapping={
        "status": "queued",
        "artifact_uuid": str(artifact.artifact_uuid),
    })

    return task_id, task_token