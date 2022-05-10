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

from rest_framework import serializers
from django.contrib.auth import password_validation
from django.contrib.auth import get_user_model

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, max_length=128)
    check_interval = serializers.CharField(required=True, max_length=128)
    continuous_alert = serializers.BooleanField(required=True)
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'password',
            'password2',
            'first_name',
            'last_name',
            'affiliation',
            'check_interval',
            'continuous_alert',
        ]
        extra_kwargs = {
            'password2': {'write_only': True}
        }

    def save(self):
        # pylint: disable = arguments-differ
        check_interval = self.validated_data.get('check_interval')

        if not check_interval:
            check_interval = 'automatic'
        elif check_interval.lower() not in ['automatic', 'weekly', 'monthly']:
            raise serializers.ValidationError({
                "error": "'{}' is not accepted! Accepted values are: "
                         "'automatic', 'weekly', 'monthly'".format(check_interval)
            })

        user = User(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
            first_name=self.validated_data.get('first_name'),
            last_name=self.validated_data.get('last_name'),
            affiliation=self.validated_data.get('affiliation'),
            check_interval=check_interval,
            continuous_alert=self.validated_data.get('continuous_alert'),
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({
                'password': 'Passwords must match!'
            })
        user.set_password(password)
        # this will become true after the account is activated using email verification
        user.is_account_activated = False
        user.save()
        return user

    def validate(self, attrs):
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({
                'email': 'Email already in use'
            })
        return super().validate(attrs)


class CustomUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, max_length=128)
    check_interval = serializers.ChoiceField(choices=['automatic', 'weekly', 'monthly'], required=True)
    continuous_alert = serializers.BooleanField(default=0)

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'affiliation',
            'check_interval',
            'continuous_alert',
        ]

    def update(self, user):
        # pylint: disable = arguments-differ
        if User.objects.filter(email=user.email).count() > 1:
            raise serializers.ValidationError({'email': 'Email already in use by another user'})

        user.email = self.validated_data.get('email')
        user.first_name = self.validated_data.get('first_name')
        user.last_name = self.validated_data.get('last_name')
        user.affiliation = self.validated_data.get('affiliation')
        user.check_interval = self.validated_data.get('check_interval')
        user.continuous_alert = self.validated_data.get('continuous_alert')
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    # pylint: disable=abstract-method)
    old_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password1 = serializers.CharField(min_length=6, max_length=128, write_only=True, required=True)
    new_password2 = serializers.CharField(min_length=6, max_length=128, write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Your old password was entered incorrectly. Please enter it again.')
        return value

    def validate(self, attrs):
        if attrs['new_password1'] != attrs['new_password2']:
            raise serializers.ValidationError({"error": "The two password fields didn't match."})
        password_validation.validate_password(attrs['new_password1'], self.context['request'].user)
        return attrs

    def save(self, **kwargs):
        password = self.validated_data['new_password1']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user


class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=128)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        return super().validate(attrs)


class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=6, max_length=128, write_only=True, required=True)
    new_password_confirm = serializers.CharField(min_length=6, max_length=128, write_only=True, required=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):

        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        uidb64 = attrs.get('uidb64')
        token = attrs.get('token')

        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                "error": "The two password fields didn't match."
            })

        id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=id)

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError({
                'error': 'The reset link is invalid'
            })

        user.set_password(new_password)
        # resetting the password automatically activates the account
        user.is_active = True
        user.save()
        return user
