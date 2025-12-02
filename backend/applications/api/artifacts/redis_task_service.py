import uuid
import json
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def enqueue_build_task(artifact):
    task_id = str(uuid.uuid4())

    task = {
        "task_id": task_id,
        "artifact_uuid": str(artifact.artifact_uuid),
        "zip_path": artifact.file.path,
        "plugin_path": "/home/pinzon/zofrenic-solutions/DeCloidMC/tests_files/server.jar",
    }

    # Empuja a Redis (cola básica)
    r.lpush("build_tasks", json.dumps(task))

    # Marca estado inicial (opcional pero MUY útil)
    r.hset(f"build_status:{task_id}", mapping={
        "status": "queued",
        "artifact_uuid": str(artifact.artifact_uuid),
    })

    return task_id
