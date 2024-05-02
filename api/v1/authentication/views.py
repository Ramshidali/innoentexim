# -*- coding: utf-8 -*-
import requests

from django.utils.html import strip_tags
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework import status

from main.functions import decrypt_message, encrypt_message, get_otp, send_email
from api.v1.authentication.serializers import ResetPasswordSerializer, UserSerializer, LogInSerializer, UserTokenObtainPairSerializer
from api.v1.authentication.functions import generate_serializer_errors, get_user_token


class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer
    
@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def login(request):
    serialized = LogInSerializer(data=request.data)

    if serialized.is_valid():

        username = serialized.data['username']
        password = serialized.data['password']

        headers = {
            'Content-Type': 'application/json',
        }
        
        data = '{"username": "' + username + '", "password":"' + password + '"}'
        protocol = "http://"
        if request.is_secure():
            protocol = "https://"

        web_host = request.get_host()
        request_url = protocol + web_host + "/api/v1/auth/token/"

        response = requests.post(request_url, headers=headers, data=data)
        
        if response.status_code == 200:
            response_data = {
                "status": status.HTTP_200_OK,
                "StatusCode": 6000,
                "data": response.json(),
                "message": "Login successfully",
                
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "status": status.HTTP_401_UNAUTHORIZED,
                "StatusCode": 6001,
                "message": "Invalid username or password",
            }

            return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)
    else:
        response_data = {
            "status": status.HTTP_400_BAD_REQUEST,
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def logout(request):
    
    request.user.auth_token.delete()
    
    response_data = {
        "status": status.HTTP_200_OK,
        "StatusCode": 6000,
        "message": "Logout successful",
        
    }
    return Response(response_data, status=status.HTTP_200_OK)