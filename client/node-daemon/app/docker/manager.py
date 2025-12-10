import docker
import uuid

class DockerManager:
    def __init__(self, base_port: int, max_port: int, logger):
        self.client = docker.from_env()
        self.base_port = base_port
        self.max_port = max_port
        self.logger = logger
        self.containers = {}  # artifact_uuid -> info

    def get_next_port(self):
        used = {info["port"] for info in self.containers.values()}
        for port in range(self.base_port, self.max_port):
            if port not in used:
                return port
        raise RuntimeError("No hay puertos disponibles")

    def create_server(self, req):
        port = req.port or self.get_next_port()
        random_suffix = uuid.uuid4().hex[:2]
        container_name = f"server_{req.artifact_uuid[:8]}_{random_suffix}"

        self.logger.info(
            f"➡ Creando servidor {container_name} en puerto {port} con {req.cpu_cores} CPUs y {req.memory_mb}MB RAM"
        )

        container = self.client.containers.run(
            image=req.image_name,
            name=container_name,
            detach=True,
            ports={"25565/tcp": port},
            mem_limit=f"{req.memory_mb}m",
            cpu_count=req.cpu_cores,
            environment={
                "MC_RAM": f"{req.memory_mb}M",
                "BACKEND_URL": req.backend_url,
                "SERVER_KEY": req.server_key},
            restart_policy={"Name": "unless-stopped"}
        )

        self.containers[req.artifact_uuid] = {
            "container_id": container.id,
            "port": port
        }

        return container, port

    def destroy_server(self, artifact_uuid):
        info = self.containers.get(artifact_uuid)
        if not info:
            return None

        container = self.client.containers.get(info["container_id"])
        container.stop()
        container.remove()
        del self.containers[artifact_uuid]

        return True

    def get_status(self, artifact_uuid):
        info = self.containers.get(artifact_uuid)
        if not info:
            return None

        container = self.client.containers.get(info["container_id"])
        return container.status, info["port"]
