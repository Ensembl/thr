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
from rest_framework import status, authentication, permissions
from rest_framework.authtoken.models import Token
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import RegistrationSerializer, CustomUserSerializer, ChangePasswordSerializer


class RegistrationViewAPI(APIView):
    """
    User registration endpoint, if the request is successful,
    an HttpResponse is returned with the access token
    :param request: the request
    :returns: the data if the request was successful otherwise it return an error message
    """

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            new_user = serializer.save()
            data['success'] = 'User registered successfully!'
            token = Token.objects.create(user=new_user).key
            data['token'] = token
            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutViewAPI(APIView):
    """
    Log the users out if they are already logged in,
    and delete the access token from the database
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Returns the response message 200 or 401 (Invalid token)
        """
        request.user.auth_token.delete()
        logout(request)
        return Response({"success": "Successfully logged out."}, status.HTTP_200_OK)


class UserDetailsView(APIView):
    """
    Get the user details when providing a valid token
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'affiliation': user.affiliation,
            'check_interval': user.check_interval,
            'continuous_alert': user.continuous_alert
        })

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        current_user = request.user

        if not request.data:
            return Response({"error": "Missing message body in request"}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.update(current_user)
            return Response({'success': 'User profile updated successfully!'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(UpdateAPIView):
    """
    Log the users out if they are already logged in,
    and delete the access token from the database
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # if using drf authtoken, create a new token
        if hasattr(user, 'auth_token'):
            user.auth_token.delete()
        token, _ = Token.objects.get_or_create(user=user)
        # return a success message with the new token
        return Response(
            {'success': 'Your password is updated successfully!', 'token': token.key},
            status=status.HTTP_200_OK
        )
