# redis_task_service.py
import uuid
import json
import redis
import jwt
from datetime import datetime, timedelta
from decloid.settings.base import SECRET_KEY

redis_pool = redis.ConnectionPool(host="localhost", port=6379, db=0, decode_responses=True)
r = redis.Redis(connection_pool=redis_pool)


class BuildInProgressError(Exception):
    pass


def enqueue_build_task(artifact, build_id=None, lock_ttl_seconds=60 * 60):
    """
    Intenta adquirir un lock por artifact. Si ya hay un build en progreso, lanza BuildInProgressError.
    Devuelve (task_id, task_token).
    """
    artifact_uuid = str(artifact.artifact_uuid)
    lock_key = f"artifact_lock:{artifact_uuid}"

    task_id = str(uuid.uuid4())

    # Intento atómico de adquirir lock
    got = r.set(lock_key, task_id, nx=True, ex=lock_ttl_seconds)
    if not got:
        current = r.get(lock_key)
        raise BuildInProgressError(f"Build already in progress for artifact {artifact_uuid} (task {current})")

    # Preparar JWT
    payload = {
        "task_id": task_id,
        "artifact_uuid": artifact_uuid,
        "exp": datetime.utcnow() + timedelta(minutes=30),
    }

    # Añadir build_id si se proporcionó
    if build_id:
        payload["build_id"] = build_id

    task_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    # Tarea completa que consume el worker
    task = {
        "task_id": task_id,
        "token": task_token,
        "artifact_uuid": artifact_uuid,
        "zip_path": artifact.zip_file.path,
    }

    if build_id:
        task["build_id"] = build_id

    # Encolar task
    r.lpush("build_tasks", json.dumps(task))

    # Estado inicial
    r.hset(f"build_status:{task_id}", mapping={
        "status": "queued",
        "artifact_uuid": artifact_uuid,
        "queued_at": datetime.utcnow().isoformat(),
        "build_id": build_id or "",
    })

    # Mapear artifact → task actual
    r.set(f"artifact_current_task:{artifact_uuid}", task_id, ex=lock_ttl_seconds)

    return task_id, task_token
