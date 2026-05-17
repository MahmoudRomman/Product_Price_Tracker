from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from collections import OrderedDict


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        
        extra_kwargs = {
            'username': {'read_only': True},
            'email': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        original_data = super().validate(attrs)
        
        custom_data = OrderedDict()
        
        custom_data['username'] = self.user.username
        custom_data['email'] = self.user.email
        custom_data['first_name'] = self.user.first_name
        custom_data['last_name'] = self.user.last_name
        
        custom_data.update(original_data)
        
        return custom_data