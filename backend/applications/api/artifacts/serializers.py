from django.conf import settings
from rest_framework import serializers
from applications.artifacts.models import Artifact
import zipfile


class ArtifactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artifact
        fields = "__all__"
        read_only_fields = [
            "artifact_uuid",
            "owner",
            "version",
        ]

    # ----------------------------
    # Validaciones principales
    # ----------------------------
    def validate(self, attrs):
        request = self.context["request"]
        user = request.user

        # ----------------------------
        # VALIDAR SUBSCRIPCIÓN
        # ----------------------------
        subscription = getattr(user, "subscription", None)
        if subscription is None:
            raise serializers.ValidationError({
                "subscription": "No tienes una suscripción activa."
            })

        # ----------------------------
        # LIMITAR CREACIÓN SEGÚN PLAN
        # ----------------------------
        if self.instance is None:
            current_count = Artifact.objects.filter(owner=user).count()
            max_allowed = getattr(subscription.plan, "max_artifacts", 0)

            if current_count >= max_allowed:
                raise serializers.ValidationError({
                    "limit": f"Has alcanzado el límite de artefactos ({max_allowed})."
                })

        # ----------------------------
        # VALIDACIÓN ZIP
        # ----------------------------
        file = attrs.get("zip_file")

        # CREACIÓN → ZIP obligatorio
        if self.instance is None and file is None:
            raise serializers.ValidationError({
                "zip_file": "Debes subir un archivo .zip para crear el artefacto."
            })

        # ACTUALIZACIÓN → ZIP opcional
        if self.instance is not None and file is None:
            return attrs

        # Validar extensión
        if file and not file.name.lower().endswith(".zip"):
            raise serializers.ValidationError({
                "zip_file": "Solo se permiten archivos .zip."
            })

        # Límite configurable en settings
        max_size_mb = getattr(settings, "ARTIFACT_MAX_ZIP_MB", 300)
        if file and file.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError({
                "zip_file": f"El archivo excede el límite de {max_size_mb}MB."
            })

        # Validar ZIP no corrupto mínimamente
        if file:
            try:
                with zipfile.ZipFile(file, "r") as z:
                    bad = z.testzip()
                    if bad:
                        raise serializers.ValidationError({
                            "zip_file": f"El archivo ZIP está corrupto (problema en {bad})."
                        })
            except zipfile.BadZipFile:
                raise serializers.ValidationError({
                    "zip_file": "El archivo proporcionado no es un ZIP válido."
                })

        return attrs

    # ----------------------------
    # CREACIÓN
    # ----------------------------
    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)

class ArtifactBuildReportSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["ready", "failed"])
    size_in_mb = serializers.FloatField(required=False, allow_null=True)
    registry_path = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    logs = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    version = serializers.CharField(required=True)
    updated_at = serializers.DateTimeField(required=False)

    def validate_version(self, value):
        # Valida formato simple semver: "1.2.3"
        import re
        if not re.match(r"^[0-9]+\.[0-9]+\.[0-9]+$", value):
            raise serializers.ValidationError("Formato de versión inválido (usa semver: X.Y.Z).")
        return value

    def validate_logs(self, value):
        if value and len(value) > 50000:
            return value[:50000] + "\n...[truncado por tamaño]"
        return value
