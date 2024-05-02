from __future__ import unicode_literals
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from six import text_type
from django.contrib.auth.models import User


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(UserTokenObtainPairSerializer, cls).get_token(user)
        return token
    
    def validate(cls, attrs):
        data = super(UserTokenObtainPairSerializer, cls).validate(attrs)

        refresh = cls.get_token(cls.user)

        data['refresh'] = text_type(refresh)
        data['access'] = text_type(refresh.access_token)

        if cls.user.is_superuser:
            data['role'] = "superuser"
        else:
            data['role'] = "user"

        return data


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username','password')

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.save()
        return user


class LogInSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
class ResetPasswordSerializer(serializers.Serializer):
    member_id = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()
    
    def member_id_validate(self, data):
        if data["member_id"] == "":
          raise serializers.ValidationError("member_id missed")

    def validate(self, data):
        password = data['password']
        confirm_password = data['confirm_password']

        if password == "":
            raise serializers.ValidationError("Enter a valid password")
        
        if confirm_password == "":
            raise serializers.ValidationError("Re-enter Password")

        if len(password) < 8:
            raise serializers.ValidationError("Password should be at least 8 characters")

        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match")

        return data

