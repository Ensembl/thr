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
import django
import jwt
from django.contrib.auth import logout
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.urls import reverse
# from django.conf import settings
from thr import settings
from rest_framework import status, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import CustomUser as User

# Token authentication is used to handle login and logout
from rest_framework.authtoken.models import Token
# JWT Authentication is used to handle account activation
# https://www.django-rest-framework.org/api-guide/authentication/#json-web-token-authentication
from rest_framework_simplejwt.tokens import RefreshToken
# https://londonappdeveloper.com/json-web-tokens-vs-token-authentication/

from django.contrib.auth import get_user_model
from users.serializers import RegistrationSerializer, CustomUserSerializer, ChangePasswordSerializer, \
    ResetPasswordEmailSerializer, SetNewPasswordSerializer

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
# Escape special HTML characters in Python
import html

User = get_user_model()


# extend the ObtainAuthToken class to add is_account_activated status to API response
class LoginViewAPI(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'email': user.email,
            'is_account_activated': user.is_account_activated
        })


class RegistrationViewAPI(APIView):
    """
    User registration endpoint, if the request is successful,
    an HttpResponse is returned and an activation email is sent with the access token
    it returns the success message if the request was successful otherwise it return an error message
    """
    def post(self, request):

        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            new_user = serializer.save()

            # token = Token.objects.create(user=new_user).key
            access_token = RefreshToken.for_user(new_user).access_token

            # prepare the data that will be sent to user
            fe_url = settings.FRONTEND_URL
            full_url = 'http://' + fe_url + "/email_verification?token=" + str(access_token)

            send_mail(
                subject='Verify your email',
                from_email='trackhub-registry@ebi.ac.uk',
                message='Hi ' + new_user.username + ' Please use the link below to verify your email \n' + full_url,
                recipient_list=[new_user.email],
                fail_silently=False
            )

            return Response(
                {'success': 'User registered successfully! A verification link has been sent to your email address'},
                status=status.HTTP_201_CREATED
            )

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    """
    Email verification endpoint, used to activate the user account
    """
    def get(self, request):
        access_token = request.GET.get('token')

        try:
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms='HS256')
            user = User.objects.get(id=payload['user_id'])
            if not user.is_account_activated:
                user.is_account_activated = True
                user.save()
            return Response({'success': 'Account activated! Please login to your account'}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError as identifier:
            return Response(
                {'error': 'This activation link is expired or have already been used!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.exceptions.DecodeError as identifier:
            return Response(
                {'error': 'Invalid token!'},
                status=status.HTTP_400_BAD_REQUEST
            )


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
            'continuous_alert': user.continuous_alert,
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


class ResetPasswordEmailView(APIView):
    """
    Endpoint allowing the user to submit their email
    to send them a password reset link
    """

    serializer_class = ResetPasswordEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            email = request.data['email']
        except django.utils.datastructures.MultiValueDictKeyError:
            return Response(
                {'error': 'Email field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if serializer.is_valid():
            user = User.objects.filter(email=email).first()
            if user:
                # encode the user id
                uidb64 = urlsafe_base64_encode(str(user.id).encode())
                # create the token
                token = PasswordResetTokenGenerator().make_token(user)

                # send the email
                fe_url = settings.FRONTEND_URL
                full_url = 'http://' + fe_url + "/reset_password?uidb64=" + uidb64 + "&token=" + token

                send_mail(
                    subject='[Trackhub Registry] Password reset',
                    from_email='trackhub-registry@ebi.ac.uk',
                    message='Hi ' + user.username + ', \nPlease use the link below to reset your password: \n' + full_url,
                    recipient_list=[user.email],
                    fail_silently=False
                )
            return Response(
                {'success': 'Please check your email, We have sent you a link to reset your password'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ValidateResetPasswordAPI(APIView):
    """
    Validate reset password token
    """

    def get(self, request):
        uidb64 = request.GET.get('uidb64')
        token = request.GET.get('token')
        try:
            # get a human readable string of user ID
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            # make sure that user isn't using this token for a second time
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    {'error': 'Token is not valid, please request a new one'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                {'success': 'Credentials are Valid', 'uidb64': html.escape(uidb64), 'token': html.escape(token)},
                status=status.HTTP_200_OK

            )

        except DjangoUnicodeDecodeError as exp:
            return Response(
                {'error': 'Token is not valid, please request a new one'},
                status=status.HTTP_400_BAD_REQUEST
            )


class SetNewPasswordAPI(APIView):
    """
    Allow the user to reset the password
    """

    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)

        return Response(
            {'success': 'Password reset successfully!'},
            status=status.HTTP_200_OK
        )
