import os
import shutil
import docker
import requests
import traceback
from datetime import datetime, timezone
from .unzipper import unzip_file
from .dockerfile_creator import create_dockerfile
from .dependency_injector import inject_plugin   # si no usas esto, bórralo

client = docker.from_env()
api_client = client.api


def process_task(task):
    """
    Ejecuta el proceso completo de construcción:
    - unzip
    - dockerfile
    - build
    - tag
    - push
    """

    artifact_uuid = task.get("artifact_uuid")
    build_id = task["task_id"]
    zip_path = task["zip_path"]
    task_token = task["token"]

    if not artifact_uuid:
        return False, "artifact_uuid faltante"

    registry_url = os.environ.get("REGISTRY_URL")
    registry_user = os.environ.get("REGISTRY_USER")
    registry_pass = os.environ.get("REGISTRY_PASS")

    backend_report_url = os.environ.get("BACKEND_REPORT_URL")
    backend_url = backend_report_url.format(task_id=build_id)

    rand = os.urandom(4).hex()
    build_dir = f"/tmp/build_{build_id}_{rand}"

    repo_name = f"{registry_url}/server_{artifact_uuid}"
    specific_tag = f"{repo_name}:{build_id}"
    latest_tag = f"{repo_name}:latest"

    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

    try:
        if registry_user and registry_pass:
            print("[LOGIN] Docker registry…")
            client.login(username=registry_user, password=registry_pass, registry=registry_url)

        print(f"[UNZIP] Extrayendo {zip_path} → {build_dir}")
        unzip_file(zip_path, build_dir)

        print("[DOCKERFILE] Generando…")
        create_dockerfile(build_dir)

        # --- Build ---
        print(f"[BUILD] Construyendo imagen {specific_tag}")
        stream = api_client.build(path=build_dir, tag=specific_tag, rm=True, decode=True)

        for chunk in stream:
            if "error" in chunk:
                raise Exception(chunk["error"])
            if "stream" in chunk:
                print(chunk["stream"].strip())

        # --- Tag :latest ---
        img = client.images.get(specific_tag)
        img.tag(repo_name, "latest")

        # --- Push ---
        def push_image(repository, tag_name):
            print(f"[PUSH] {repository}:{tag_name}")
            push_stream = api_client.push(repository, tag=tag_name, stream=True, decode=True)
            for piece in push_stream:
                if "error" in piece:
                    raise Exception(piece["error"])
                if "status" in piece:
                    print(piece["status"])

        push_image(repo_name, build_id)
        push_image(repo_name, "latest")

        return True, {
            "version": build_id,
            "size_mb": os.path.getsize(zip_path) // (1024 * 1024),
            "registry_path": specific_tag,
            "logs": f"Build OK: {specific_tag}",
            "hash": None,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        traceback.print_exc()
        return False, f"Error: {str(e)}"

    finally:
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
