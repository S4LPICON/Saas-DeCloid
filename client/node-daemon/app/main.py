from fastapi import FastAPI
from app.core.config import config
from app.core.logging import setup_logger
from app.docker.manager import DockerManager
from app.api.routes_servers import init_routes as routes_servers
from app.api.routes_status import init_routes as routes_status

from app.heartbeat.heartbeat import start_heartbeat  # importa tu función

logger = setup_logger()
app = FastAPI(title="Nodo DeCloid Daemon")

print("Starting DeCloid Daemon...")

manager = DockerManager(
    base_port=config["docker"]["base_port"],
    max_port=config["docker"]["max_port"],
    logger=logger
)

app.include_router(
    routes_servers(manager, config["node"]["key"]),
    prefix=""
)
app.include_router(
    routes_status(manager, config["node"]["key"]),
    prefix=""
)

# --------- AQUI ARRANCA EL HEARTBEAT ---------
@app.on_event("startup")
def start_node_heartbeat():
    start_heartbeat(
    node_id=config["node"]["uuid"],
    backend_url=f"{config['remote']}/api/v1/nodes/{config['node']['uuid']}/heartbeat/",
    node_key=config["node"]["key"],
    interval=15   # cada 15s
    )
