"""
.. See the NOTICE file distributed with this work for additional information
   regarding copyright ownership.
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

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
