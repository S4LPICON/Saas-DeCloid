import requests
#TOD: OJO que quedan repos huerfanos en el registry

def delete_artifact_from_registry(server_id, registry_url="http://localhost:5000"):
    """
    Borra TODAS las referencias (tags y manifiestos) de un repositorio en el Registry.
    """
    repo_name = f"server_{server_id}"
    api_base = f"{registry_url}/v2"
    
    print(f"Iniciando borrado del repositorio: {repo_name}")

    try:
        # 1. Obtener lista de tags
        tags_url = f"{api_base}/{repo_name}/tags/list"
        r = requests.get(tags_url)
        
        if r.status_code == 404:
            print("l repositorio ya no existe o ya fue borrado.")
            return True # Consideramos éxito porque ya no está

        data = r.json()
        tags = data.get("tags", [])

        if not tags:
            print("El repositorio existe pero no tiene tags.")
            return True

        # 2. Recolectar los Digests únicos
        # Usamos un set() porque 'latest' y el 'uuid' suelen apuntar al MISMO digest.
        # Si intentas borrar el mismo digest dos veces, dará error 404.
        digests_to_delete = set()

        for tag in tags:
            # HEAD request para obtener el Docker-Content-Digest
            # OJO: Es CRÍTICO enviar el header 'Accept' correcto
            headers = {'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
            manifest_url = f"{api_base}/{repo_name}/manifests/{tag}"
            
            head_req = requests.head(manifest_url, headers=headers)
            digest = head_req.headers.get('Docker-Content-Digest')
            
            if digest:
                digests_to_delete.add(digest)

        # 3. Borrar cada Digest
        for digest in digests_to_delete:
            delete_url = f"{api_base}/{repo_name}/manifests/{digest}"
            del_req = requests.delete(delete_url)
            
            if del_req.status_code == 202:
                print(f"Digest eliminado: {digest}")
            else:
                print(f"Error al borrar digest {digest}: {del_req.status_code}")

        return True

    except Exception as e:
        print(f"Error crítico conectando al registry: {e}")
        return False