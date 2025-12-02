import redis, json, subprocess, os

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def dispatch_task(task):
    # Carpeta del worker
    worker_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../worker")
    )

    # Lanza el worker como subproceso usando -m para que Python reconozca src
    subprocess.Popen(
        ["python", "-m", "src.queue.run_worker_task", json.dumps(task)],
        cwd=worker_path
    )

def listen_redis():
    print("Manager escuchando Redis...")
    while True:
        task_str = r.brpop("build_tasks", timeout=5)
        if task_str:
            _, task_json = task_str
            task = json.loads(task_json)
            print("Tarea recibida:", task["task_id"])
            dispatch_task(task)

if __name__ == "__main__":
    listen_redis()
