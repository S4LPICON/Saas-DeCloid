import redis, json

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
task = {
    "id": "delete_me",
    "zip_path": "/home/pinzon/zofrenic-solutions/DeCloidMC/tests_files/server.zip",
    "plugin_path": "/home/pinzon/zofrenic-solutions/DeCloidMC/tests_files/server.jar"
}
r.lpush("build_tasks", json.dumps(task))
print("Tarea enviada a Redis")
