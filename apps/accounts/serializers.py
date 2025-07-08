from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.shortcuts import redirect
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('latitude', 'longitude')

class UserSerializer(serializers.ModelSerializer):
    token = serializers.CharField(source='auth_token.key', read_only=True)
    latitude = serializers.DecimalField(source='profile.latitude', max_digits=9, decimal_places=6, required=False, allow_null=True)
    longitude = serializers.DecimalField(source='profile.longitude', max_digits=9, decimal_places=6, required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'token', 'latitude', 'longitude', )

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        instance = super().update(instance, validated_data)
        profile, created = Profile.objects.get_or_create(user=instance)
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()
        return instance
