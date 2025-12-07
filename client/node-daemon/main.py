from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
import docker
import uuid
import logging

# Configuración básica
NODE_KEY = "supersecreto-nodo"  # Clave para autenticar al orquestador
BASE_PORT = 25565  # Puerto inicial para Minecraft
MAX_PORT = 25600   # Puerto máximo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NodoDaemon")

app = FastAPI(title="Nodo DeCloid Daemon")
client = docker.from_env()

# Map de artifact_uuid -> container info
containers = {}

# Modelo para crear servidor
class ServerRequest(BaseModel):
    artifact_uuid: str
    image_name: str = Field(..., description="Nombre de la imagen Docker")
    memory_mb: int = Field(512, ge=128)
    cpu_cores: int = Field(1, ge=1)
    port: int | None = Field(None, description="Si no se especifica, se asigna automáticamente")

def get_next_available_port():
    used_ports = {info['port'] for info in containers.values()}
    for port in range(BASE_PORT, MAX_PORT):
        if port not in used_ports:
            return port
    raise RuntimeError("No hay puertos disponibles")

def authenticate(x_node_key: str | None):
    if x_node_key != NODE_KEY:
        raise HTTPException(status_code=403, detail="Clave de nodo inválida")

# Crear servidor
@app.post("/create-server")
def create_server(req: ServerRequest, x_node_key: str | None = Header(None)):
    print("intentando crear servidor...")
    authenticate(x_node_key)
    port = req.port or get_next_available_port()
    random_suffix = uuid.uuid4().hex[:2]
    container_name = f"server_{req.artifact_uuid[:8]}_{random_suffix}"

    logger.info(f"➡ Creando servidor {container_name} en puerto {port} con {req.cpu_cores} CPUs y {req.memory_mb}MB RAM")

    try:
        container = client.containers.run(
            image=req.image_name,
            name=container_name,
            detach=True,
            ports={"25565/tcp": port},
            mem_limit=f"{req.memory_mb}m",
            cpu_count=req.cpu_cores,
            environment={"MC_RAM": f"{req.memory_mb}M"},
            restart_policy={"Name": "unless-stopped"}
        )

        containers[req.artifact_uuid] = {"container_id": container.id, "port": port}
        return {"status": "ok", "container_id": container.id, "port": port, "ip_address": ""}
    except docker.errors.DockerException as e:
        logger.error(f"Error creando contenedor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Detener y eliminar servidor
@app.post("/destroy-server/{artifact_uuid}")
def destroy_server(artifact_uuid: str, x_node_key: str | None = Header(None)):
    authenticate(x_node_key)
    info = containers.get(artifact_uuid)
    if not info:
        raise HTTPException(status_code=404, detail="Servidor no encontrado")
    try:
        container = client.containers.get(info['container_id'])
        container.stop()
        container.remove()
        del containers[artifact_uuid]
        logger.info(f"🛑 Servidor {artifact_uuid} destruido")
        return {"status": "ok"}
    except docker.errors.DockerException as e:
        logger.error(f"Error destruyendo contenedor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Estado del servidor
@app.get("/status/{artifact_uuid}")
def status_server(artifact_uuid: str, x_node_key: str | None = Header(None)):
    authenticate(x_node_key)
    info = containers.get(artifact_uuid)
    if not info:
        return {"status": "not_found"}
    try:
        container = client.containers.get(info['container_id'])
        return {"status": container.status, "port": info["port"]}
    except docker.errors.DockerException:
        return {"status": "error"}
