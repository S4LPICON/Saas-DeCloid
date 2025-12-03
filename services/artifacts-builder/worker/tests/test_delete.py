import os
import requests

def force_delete_repo(uuid_target, registry_url="http://localhost:5000", registry_storage_path="/var/lib/registry/docker/registry/v2/repositories"):
    """
    Borra completamente un repositorio de Docker Registry, incluso si no tiene tags.
    """
    repo_name = f"server_{uuid_target}"
    api_base = f"{registry_url}/v2"
    
    print(f"🔥 ATACANDO REPO: {repo_name}")

    try:
        # 1. Intentamos obtener tags visibles
        tags_url = f"{api_base}/{repo_name}/tags/list"
        r = requests.get(tags_url)
        tags = r.json().get("tags") or []

        digests_to_delete = set()

        headers = {'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}

        # 2a. Digests desde tags visibles
        for tag in tags:
            print(f"   🔍 Procesando tag: {tag}")
            manifest_url = f"{api_base}/{repo_name}/manifests/{tag}"
            head_req = requests.head(manifest_url, headers=headers)
            digest = head_req.headers.get('Docker-Content-Digest')
            if digest:
                digests_to_delete.add(digest)
                print(f"   🔎 Digest encontrado para tag {tag}: {digest}")

        # 2b. Digests huérfanos desde filesystem
        repo_path = os.path.join(registry_storage_path, repo_name, "_manifests", "revisions", "sha256")
        if os.path.exists(repo_path):
            for digest_file in os.listdir(repo_path):
                digest = f"sha256:{digest_file}"
                digests_to_delete.add(digest)
                print(f"   🔎 Digest huérfano encontrado en filesystem: {digest}")

        if not digests_to_delete:
            print("💀 No se encontraron digests para borrar. Tal vez el repo ya estaba vacío.")
            return

        # 3. Borrar cada digest
        for digest in digests_to_delete:
            delete_url = f"{api_base}/{repo_name}/manifests/{digest}"
            del_req = requests.delete(delete_url)
            if del_req.status_code == 202:
                print(f"   ✅ Digest eliminado: {digest}")
            elif del_req.status_code == 405:
                print(f"   ⛔ ERROR 405: Borrado desactivado en config")
            else:
                print(f"   ❌ Falló borrado {digest}, código: {del_req.status_code}")

        print("💀 Borrado completado. Ahora ejecuta garbage-collect para liberar espacio físico.")
        print(f"docker exec -i registry bin/registry garbage-collect /etc/docker/registry/config.yml")

    except Exception as e:
        print(f"❌ Error crítico: {e}")


# Ejemplo de uso
force_delete_repo("aaf79668-b9e1-454a-98c7-d4b07872428f")
