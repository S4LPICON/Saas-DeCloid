artifacts_builder_manager/
├── src/
│   ├── api/                  # Endpoints HTTP
│   │   └── build_tasks.py    # Endpoint para crear nuevas tareas
│   ├── queue/                # Interacción con Redis
│   │   └── redis_client.py
│   ├── services/
│   │   ├── task_dispatcher.py # Lógica de enviar tareas a workers
│   │   └── task_listener.py   # Escucha resultados de los workers
│   ├── models/               # DTOs / schemas de tareas
│   └── utils/                # Logs, helpers, validaciones
├── tests/
├── Dockerfile
├── requirements.txt / pyproject.toml
└── README.md
