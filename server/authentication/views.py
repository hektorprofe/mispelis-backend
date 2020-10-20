from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class LoginView(APIView):

    def post(self, request):
        # Creamos una respuesta básica
        response = {'login': 'fail'}

        # # Recuperamos las credenciales y autenticamos al usuario
        email = request.data.get('email', None)
        password = request.data.get('password', None)
        user = authenticate(email=email, password=password)

        # Si es correcto añadimos a la request la información de sesión
        if user:
            login(request, user)
            response['login'] = 'success'

        # Devolvemos la respuesta al cliente
        return Response(
            response, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request):
        # Borramos de la request la información de sesión
        logout(request)

        # Devolvemos la respuesta al cliente
        return Response(
            {'logout': 'success'}, status=status.HTTP_200_OK)
