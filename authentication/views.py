from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from authentication.serializers import UserSerializer, UserLoginSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class RegistrationView(APIView):
    """
    View for registering a new user to your system.

    **Example requests**:

        POST /api/auth/register/
    """

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT, 
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='test@yopmail.com'),
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
        }
    ))
    @transaction.atomic()
    def post(self, request):
        email = request.data.get('email', None)
        UserModel = get_user_model()

        try:
            users = UserModel.objects.filter(email=email)
            if (len(users) >= 1):
                return Response("Email exist", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        except UserModel.DoesNotExist:
            pass

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    """
    View for login a user to your system.

    **Example requests**:

        POST /api/auth/login/
    """

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT, 
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
        }
    ))
    def post(self, request):
        email = request.data.get('email', None)
        password = request.data.get('password', None)

        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return Response("Email not exist", status=status.HTTP_404_NOT_FOUND)
    
        authenticated_user = authenticate(username=user.get_username(), password=password)
        if authenticated_user:
            serializer = UserLoginSerializer(authenticated_user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response("Invalid Credentials", status=status.HTTP_401_UNAUTHORIZED)