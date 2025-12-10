from pydantic import BaseModel, Field

class ServerRequest(BaseModel):
    backend_url: str
    server_key: str
    artifact_uuid: str
    image_name: str = Field(..., description="Nombre de la imagen Docker")
    memory_mb: int = Field(512, ge=128)
    cpu_cores: int = Field(1, ge=1)
    port: int | None = Field(None, description="Si no se especifica, se asigna automáticamente")
