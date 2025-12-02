import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings

class ArtifactStorage(FileSystemStorage):
    """
    Almacenamiento físico para los artifacts fuera del proyecto Django,
    usando la ruta base ARTIFACTS_ROOT.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            location=settings.ARTIFACTS_ROOT,
            base_url=None,
            *args,
            **kwargs
        )

    def get_available_name(self, name, max_length=None):
        # NO sobrescribas archivos automáticamente
        if self.exists(name):
            raise FileExistsError(f"El archivo '{name}' ya existe.")
        return name
