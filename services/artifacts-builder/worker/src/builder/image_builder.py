import docker
import os
import shutil
from .unzipper import unzip_file
from .dockerfile_creator import create_dockerfile
from .dependency_injector import inject_plugin


client = docker.from_env()

def process_task(task):
    """
    Procesa una tarea de build real:
    - Descomprime zip
    - Inyecta plugin
    - Crea Dockerfile
    - Construye imagen Docker
    - Hace push al registry
    """
    build_id = task["task_id"]
    zip_path = task["zip_path"]
    plugin_path = task["plugin_path"]
    registry_url = os.environ.get("REGISTRY_URL", "localhost:5000")
    rand = str(os.urandom(4).hex())
    build_dir = f"/tmp/build_{build_id} + {rand}"

    # Limpieza de build anterior
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

    try:
        # 1️⃣ Descomprimir ZIP
        unzip_file(zip_path, build_dir)

        # 2️⃣ Inyectar plugin
        inject_plugin(build_dir, plugin_path)

        # 3️⃣ Crear Dockerfile
        create_dockerfile(build_dir)

        # 4️⃣ Construir imagen
        image_tag = f"{registry_url}/server_{build_id}:latest"
        print(f"Construyendo imagen: {image_tag}")
        image, logs = client.images.build(path=build_dir, tag=image_tag)
        for chunk in logs:
            if 'stream' in chunk:
                print(chunk['stream'].strip())

        # 5️⃣ Push al registry
        print(f"Haciendo push de la imagen al registry: {registry_url}")
        client.images.push(image_tag)

        return True, f"Build completo y pushed: {image_tag}"

    except docker.errors.BuildError as e:
        return False, f"BuildError: {str(e)}"
    except docker.errors.APIError as e:
        return False, f"DockerAPIError: {str(e)}"
    except FileNotFoundError as e:
        return False, f"FileNotFound: {str(e)}"
    except Exception as e:
        return False, f"UnexpectedError: {str(e)}"
    finally:
        # Limpieza opcional del directorio temporal
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
