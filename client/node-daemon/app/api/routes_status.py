from fastapi import APIRouter, Header
from app.core.security import authenticate

router = APIRouter()

def init_routes(manager, node_key):

    @router.get("/status/{artifact_uuid}")
    def status_server(artifact_uuid: str, x_node_key: str | None = Header(None)):
        authenticate(x_node_key, node_key)

        status = manager.get_status(artifact_uuid)
        if not status:
            return {"status": "not_found"}

        docker_status, port = status
        return {"status": docker_status, "port": port}

    return router
