import json
from src.builder.image_builder import process_task

# Crear tarea manualmente
task = {
    "id": "test1",
    "zip_path": "/home/pinzon/zofrenic-solutions/DeCloidMC/tests_files/server.zip",
    "plugin_path": "/home/pinzon/zofrenic-solutions/DeCloidMC/tests_files/server.jar"
}

# Ejecutar build
success, output = process_task(task)

# Mostrar resultado
print("Éxito:", success)
print("Output:", output)
