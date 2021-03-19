from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True)
    username = serializers.CharField(
        required=True)
    password = serializers.CharField(
        min_length=8, write_only=True)
    avatar = serializers.ImageField(
        required=False, allow_null=True)

    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'password', 'avatar')  # edited

    def validate_password(self, value):
        return make_password(value)

    def validate_username(self, value):
        value = value.replace(" ", "")  # Ya que estamos borramos los espacios
        try:
            user = get_user_model().objects.get(username=value)
            # Si es el mismo usuario mandando su mismo username le dejamos
            if user == self.instance:
                return value
        except get_user_model().DoesNotExist:
            return value
        raise serializers.ValidationError("Nombre de usuario en uso")

    def validate_email(self, value):
        # Hay un usuario con este email ya registrado?
        try:
            user = get_user_model().objects.get(email=value)
        except get_user_model().DoesNotExist:
            return value
        # En cualquier otro caso la validación fallará
        raise serializers.ValidationError("Email en uso")

    def update(self, instance, validated_data):
        validated_data.pop('email', None)               # prevenimos el borrado
        return super().update(instance, validated_data)  # seguimos la ejecución
