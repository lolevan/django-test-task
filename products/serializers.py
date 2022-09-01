from rest_framework import serializers

from django.contrib.auth import authenticate

from .models import User, Products


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        min_length=8,
        max_length=128,
        write_only=True
    )

    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'token']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)

        if email is None:
            raise serializers.ValidationError(
                'Для входа в систему требуется email'
            )
        if password is None:
            raise serializers.ValidationError(
                'Для входа в систему требуется пароль'
            )

        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError(
                'Некорректные данные для входа в учетную запись'
            )
        if not user.is_active:
            raise serializers.ValidationError(
                'Подтвердите свою почту'
            )

        return {
            'email': user.email,
            'token': user.token,
        }


class ProductsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Products
        fields = ['name', 'desc', 'price']
