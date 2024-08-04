"""serializers for users app"""
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from .models import CustomUser, Profile
from django.utils.translation import gettext as _
import json

User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ['user']

class CustomUserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password1', 'password2', 'profile']
        read_only_fields = ('id',)

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = CustomUser.objects.create_user(**validated_data)
        Profile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        profile = instance.profile

        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        profile.address = profile_data.get('address', profile.address)
        profile.phone_number = profile_data.get('phone_number', profile.phone_number)
        profile.save()

        return instance


class LoginSerializer(serializers.Serializer):
    """validate the user credentials"""
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(
        label=_("Password"),
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = User.objects.filter(username=username).first()

            if user and user.check_password(password):
                refresh = RefreshToken.for_user(user)

                data = {
                    'username': user.username,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                }
                return data
            else:
                raise AuthenticationFailed('Invalid credentials')
        else:
            raise serializers.ValidationError('Username and password are required')
