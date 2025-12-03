import os

def create_dockerfile(build_dir):
    dockerfile_path = os.path.join(build_dir, "Dockerfile")

    dockerfile_content = """
    FROM eclipse-temurin:21-jdk

    WORKDIR /server

    # Copiar todo
    COPY . /server

    # Aceptar EULA
    RUN echo "eula=true" > /server/eula.txt

    # Buscar automáticamente el JAR del servidor
    RUN SERVER_JAR=$(find . -maxdepth 3 -type f -iname "*.jar" | grep -E "paper|purpur|spigot|fabric|forge" | head -n 1) \
        && echo "Detectado JAR: $SERVER_JAR" \
        && echo "$SERVER_JAR" > server_launcher_path

    EXPOSE 25565

    # RAM dinámica vía variable de entorno MC_RAM (ej: 2G, 3G)
    CMD ["sh", "-c", "java -Xms${MC_RAM:-1G} -Xmx${MC_RAM:-2G} -jar $(cat server_launcher_path) nogui"]
    """

    with open(dockerfile_path, "w") as f:
        f.write(dockerfile_content.strip())

    return dockerfile_path
