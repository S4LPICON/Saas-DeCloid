import uvicorn
import yaml

with open("config.yml") as f:
    cfg = yaml.safe_load(f)

uvicorn.run(
    "app.main:app",
    host=cfg["api"]["host"],
    port=cfg["api"]["port"],
)
