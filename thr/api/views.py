from django.contrib.auth import logout
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import RegistrationSerializer


@api_view(['POST'])
def registration_view(request):
    """
    User registration endpoint, if the request is successful,
    the response is formatted as a JSON object with a response message
    and an access token
    :param request: the request
    :returns: the data if the request was successful otherwise it return an error message
    """
    serializer = RegistrationSerializer(data=request.data)
    data = {}
    if serializer.is_valid():
        new_user = serializer.save()
        data['response'] = 'User registered Successfully!'
        token = Token.objects.get(user=new_user).key
        data['token'] = token
        return Response(serializer.errors, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def logout_view(request):
    """
    Log the user out if he/she is already logged in,
    and delete the access token from the database
    :param request: the request
    :returns: the response message
    """
    request.user.auth_token.delete()
    logout(request)
    return Response({"success": "Successfully logged out."}, status.HTTP_200_OK)
