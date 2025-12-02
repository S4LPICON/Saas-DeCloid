artifacts_builder_worker/
├── src/
│   ├── queue/                # Escucha de Redis
│   │   └── redis_listener.py
│   ├── builder/              # Lógica de construcción
│   │   ├── unzipper.py       # Descomprime el zip
│   │   ├── dockerfile_creator.py # Genera Dockerfile
│   │   ├── dependency_injector.py # Inyecta plugins/deps
│   │   └── image_builder.py  # Hace build y push de la imagen
│   ├── models/               # DTOs / schemas de tareas
│   └── utils/                # Logs, manejo de errores, helpers
├── tests/
├── Dockerfile
├── requirements.txt / pyproject.toml
└── README.md

REDIS_HOST=
REDIS_PORT=
REGISTRY_URL=