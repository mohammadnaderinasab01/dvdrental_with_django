from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password', 'is_customer')
        read_only_fields = ['id']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserUpdateSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password', 'is_customer')
        read_only_fields = ['id', 'email', 'is_customer']
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class UserLoginSerializer(UserSerializer):
    token = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = ('token',)

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        tokens = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
        return tokens


class UserSignupSerializerRequest(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'is_customer']


class UserLoginSerializerRequest(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']
