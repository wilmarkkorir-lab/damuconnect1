from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role', 'phone')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_role(self, value):
        if value == 'admin':
            raise serializers.ValidationError("Admin accounts cannot be self-registered.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        # Pass request to authenticate so django-axes can track failed attempts
        request = self.context.get('request')
        user = authenticate(request=request, username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials. Please try again.")
        if not user.is_active:
            raise serializers.ValidationError("This account has been deactivated.")
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    # Safe read-only representation of a user — returned after login/register
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'phone')


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'phone')

    def validate_email(self, value):
        user = self.instance
        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No account found with this email.")
        return value

    def get_reset_data(self):
        user = User.objects.get(email=self.validated_data['email'])
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        return uid, token


class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        try:
            pk = force_str(urlsafe_base64_decode(data['uid']))
            user = User.objects.get(pk=pk)
        except (User.DoesNotExist, ValueError):
            raise serializers.ValidationError("Invalid reset link.")
        if not default_token_generator.check_token(user, data['token']):
            raise serializers.ValidationError("Reset link is invalid or has expired.")
        data['user'] = user
        return data
