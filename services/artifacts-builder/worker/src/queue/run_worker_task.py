import sys, json
from src.builder.image_builder import process_task

if len(sys.argv) < 2:
    print("Se requiere un argumento: tarea JSON")
    sys.exit(1)

task = json.loads(sys.argv[1])
success, output = process_task(task)

# Reporta al manager (simple print por ahora)
if success:
    print(f"✅ Build exitoso: {task['task_id']}")
    print(output)
    #reportar exito al manager
    
    """
    version
    status: builded
    size_in_mb
    registry_path
    logs_path
    hash_value
    update-date
    """
else:
    print(f"❌ Build fallido: {task['task_id']}")
    print(output)
    #reportar fallo al manager
