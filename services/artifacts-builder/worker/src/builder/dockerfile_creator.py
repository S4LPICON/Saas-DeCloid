import os

def create_dockerfile(build_dir, base_image="alpine:latest"):
    dockerfile_path = os.path.join(build_dir, "Dockerfile")
    dockerfile_content = f"""
    FROM {base_image}
    WORKDIR /app
    COPY . /app
    RUN echo "Simulando build..."  # en lugar de gradlew/mvnw
    CMD ["echo", "Build completo"]
    """
    with open(dockerfile_path, "w") as f:
        f.write(dockerfile_content.strip())
    return dockerfile_path
