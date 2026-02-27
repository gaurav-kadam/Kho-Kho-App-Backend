from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password

class SignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'role',
            'phone_number',
            'gender',
            'state',
            'city'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)