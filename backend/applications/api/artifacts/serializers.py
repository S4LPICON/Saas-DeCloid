from rest_framework import serializers
from applications.artifacts.models import Artifact
from rest_framework import serializers

class ArtifactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artifact
        fields = "__all__"
        read_only_fields = [
            "artifact_uuid",
            "owner",
            "version",
        ]

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user

        # 1. Validar suscripción
        subscription = user.subscription
        if subscription is None:
            raise serializers.ValidationError("No tienes una suscripción activa.")

        # 2. Validar límite en creación
        if self.instance is None:
            current_count = Artifact.objects.filter(owner=user).count()
            if current_count >= subscription.plan.max_artifacts:
                raise serializers.ValidationError(
                    f"Has alcanzado el límite de artefactos ({subscription.plan.max_artifacts})."
                )

        # 3. Validación del archivo ZIP
        file = attrs.get("zip_file")

        if self.instance is None:
            # CREACIÓN -> ZIP obligatorio
            if file is None:
                raise serializers.ValidationError("Debes subir un archivo .zip")
        else:
            # ACTUALIZACIÓN -> ZIP opcional
            if file is None:
                return attrs  # No toca ZIP → validación terminada

        # Si viene archivo, validarlo
        if file and not file.name.lower().endswith(".zip"):
            raise serializers.ValidationError("Solo se permiten archivos .zip")

        max_size_mb = 300
        if file and file.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(
                f"El archivo excede el límite de {max_size_mb}MB."
            )

        return attrs


    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)



class ArtifactBuildReportSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=["ready", "failed"],
        required=True
    )
    size_in_mb = serializers.FloatField(required=False, allow_null=True)
    registry_path = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    logs = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    version = serializers.CharField(required=True)  # 🔥 obligatorio
    updated_at = serializers.DateTimeField(required=False)
