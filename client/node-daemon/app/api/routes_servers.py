from fastapi import APIRouter, Header, HTTPException
from app.core.security import authenticate
from app.models.server_request import ServerRequest

router = APIRouter()

def init_routes(manager, node_key):
    
    @router.post("/create-server")
    def create_server(req: ServerRequest, x_node_key: str | None = Header(None)):
        authenticate(x_node_key, node_key)

        try:
            container, port = manager.create_server(req)
            return {
                "status": "ok",
                "container_id": container.id,
                "port": port,
                "ip_address": ""
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/destroy-server/{artifact_uuid}")
    def destroy_server(artifact_uuid: str, x_node_key: str | None = Header(None)):
        authenticate(x_node_key, node_key)

        ok = manager.destroy_server(artifact_uuid)
        if not ok:
            raise HTTPException(status_code=404, detail="Servidor no encontrado")

        return {"status": "ok"}

    return router
