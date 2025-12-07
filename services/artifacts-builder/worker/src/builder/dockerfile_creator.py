import os

def create_dockerfile(build_dir):
    dockerfile_path = os.path.join(build_dir, "Dockerfile")

    dockerfile_content = """
    FROM eclipse-temurin:21-jdk

    WORKDIR /server
    
    COPY . /server

    RUN echo "eula=true" > eula.txt

    EXPOSE 25565

    # CMD directo al JAR que ya tienes
    CMD ["sh", "-c", "java -Xms${MC_RAM:-1G} -Xmx${MC_RAM:-2G} -jar server.jar nogui"]
    """

    with open(dockerfile_path, "w") as f:
        f.write(dockerfile_content.strip())

    return dockerfile_path
