import os
import shutil
import docker
import requests
import traceback
from .unzipper import unzip_file
from .dockerfile_creator import create_dockerfile
from .dependency_injector import inject_plugin
from datetime import datetime, timezone

# Cliente Docker (alto nivel + low level)
client = docker.from_env()
api_client = client.api


def process_task(task):
    """
    Procesa una tarea de build enviada desde Redis.
    Construye la imagen, la etiqueta, hace push al registry
    y reporta al backend.
    """

    artifact_uuid = task.get("artifact_uuid")
    build_id = task["task_id"]
    zip_path = task["zip_path"]
    plugin_path = task["plugin_path"]
    task_token = task["token"]  # 🔥 IMPORTANTE

    if not artifact_uuid:
        print("[ERROR] artifact_uuid faltante", flush=True)
        return False, "Error: artifact_uuid faltante"

    registry_url = os.environ.get("REGISTRY_URL")
    registry_user = os.environ.get("REGISTRY_USER")
    registry_pass = os.environ.get("REGISTRY_PASS")

    backend_report = os.environ.get("BACKEND_REPORT_URL")
    if not backend_report:
        raise RuntimeError("BACKEND_REPORT_URL no está definido en variables de entorno")

    backend_url = backend_report.format(task_id=build_id)

    rand = os.urandom(4).hex()
    build_dir = f"/tmp/build_{build_id}_{rand}"

    repo_name = f"{registry_url}/server_{artifact_uuid}"
    specific_tag = f"{repo_name}:{build_id}"
    latest_tag = f"{repo_name}:latest"

    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

    try:
        # 0️⃣ Login
        if registry_user and registry_pass:
            print("[DEBUG] Haciendo login en Docker…", flush=True)
            client.login(username=registry_user, password=registry_pass, registry=registry_url)

        # 1️⃣ Unzip
        print(f"[DEBUG] Descomprimiendo {zip_path} en {build_dir}…", flush=True)
        unzip_file(zip_path, build_dir)

        # 2️⃣ Inyección plugin
        print(f"[DEBUG] Inyectando plugin {plugin_path}…", flush=True)
        inject_plugin(build_dir, plugin_path)

        # 3️⃣ Dockerfile
        print(f"[DEBUG] Creando Dockerfile en {build_dir}…", flush=True)
        create_dockerfile(build_dir)

        # 4️⃣ Build
        print(f"[DEBUG] Construyendo imagen {specific_tag}…", flush=True)
        stream = api_client.build(path=build_dir, tag=specific_tag, rm=True, decode=True)
        for chunk in stream:
            if "error" in chunk:
                print(f"[DEBUG] Error en build: {chunk['error']}", flush=True)
                raise Exception(chunk["error"])
            if "stream" in chunk:
                print(chunk["stream"].strip(), flush=True)

        # 5️⃣ Tag latest
        print(f"[DEBUG] Etiquetando imagen {specific_tag} como latest…", flush=True)
        img = client.images.get(specific_tag)
        img.tag(repo_name, "latest")

        # 6️⃣ Push
        def push_image(repository, tag_name):
            print(f"[DEBUG] Subiendo {repository}:{tag_name}…", flush=True)
            push_stream = api_client.push(repository, tag=tag_name, stream=True, decode=True)
            for piece in push_stream:
                if "error" in piece:
                    err = piece.get("error") or piece.get("errorDetail", {}).get("message")
                    raise Exception(f"Error durante push: {err}")
                if "status" in piece:
                    print(f"[PUSH] {piece['status']}", flush=True)

        push_image(repo_name, build_id)
        push_image(repo_name, "latest")

        # 7️⃣ Report SUCCESS al backend
        payload = {
            "status": "active",
            "version": build_id,  # <--- Asegúrate de esto
            "size_in_mb": os.path.getsize(zip_path) // (1024*1024),
            "registry_path": specific_tag,
            "logs": f"Build OK. Imagen: {specific_tag}",
            "hash_value": None,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        headers = {
            "X-TASK-TOKEN": task_token,
            "Content-Type": "application/json",
        }

        print(f"[DEBUG] Enviando reporte SUCCESS -> {backend_url}", flush=True)
        resp = requests.post(backend_url, json=payload, headers=headers)
        print(f"[DEBUG] Backend respondió: {resp.status_code} {resp.text}", flush=True)

        return True, {
            "version": build_id,
            "size_mb": os.path.getsize(zip_path) // (1024 * 1024),
            "registry_path": specific_tag,
            "logs": f"Build OK. Imagen: {specific_tag}",
            "hash": None,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }


    except Exception as e:
        print(f"❌ ERROR en proceso: {e}", flush=True)
        traceback.print_exc()

        # 8️⃣ Report ERROR al backend
        try:
            headers = {"X-TASK-TOKEN": task_token, "Content-Type": "application/json"}
            resp = requests.post(
                backend_url,
                json={"status": "error", "message": str(e)},
                headers=headers
            )
            print(f"[DEBUG] Backend report ERROR respondió: {resp.status_code} {resp.text}", flush=True)
        except Exception as inner_e:
            print(f"[DEBUG] No se pudo reportar error al backend: {inner_e}", flush=True)

        return False, f"Error: {str(e)}"

    finally:
        # 9️⃣ Limpieza
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        try:
            client.images.remove(specific_tag)
        except:
            pass
        try:
            client.images.remove(latest_tag)
        except:
            pass
