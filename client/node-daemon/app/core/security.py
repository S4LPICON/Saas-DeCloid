from fastapi import HTTPException

def authenticate(x_node_key: str | None, node_key: str):
    if x_node_key != node_key:
        raise HTTPException(status_code=403, detail="Clave de nodo inválida")
