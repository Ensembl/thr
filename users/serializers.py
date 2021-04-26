from users.models import CustomUser
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = CustomUser
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
        check_interval = self.validated_data.get('check_interval')

        if not check_interval:
            check_interval = 'automatic'
        elif check_interval.lower() not in ['automatic', 'weekly', 'monthly']:
            raise serializers.ValidationError({
                "error": "'{}' is not accepted! Accepted values are: "
                         "'automatic', 'weekly', 'monthly'".format(check_interval)
            })

        user = CustomUser(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
            first_name=self.validated_data.get('first_name'),
            last_name=self.validated_data.get('last_name'),
            affiliation=self.validated_data.get('affiliation'),
            check_interval=check_interval,
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({
                'password': 'Passwords must match!'
            })
        user.set_password(password)
        user.save()
        return user

    def validate(self, attrs):
        if CustomUser.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({
                'email': 'Email already in use'
            })
        return super().validate(attrs)


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'first_name',
            'last_name',
            'affiliation',
            'check_interval',
            'continuous_alert',
        ]

    def update(self, user):
        if CustomUser.objects.filter(email=user.email).count() > 1:
            raise serializers.ValidationError({'email': 'Email already in use by another user'})

        user.email = self.validated_data.get('email')
        user.first_name = self.validated_data.get('first_name')
        user.last_name = self.validated_data.get('last_name')
        user.affiliation = self.validated_data.get('affiliation')
        user.check_interval = self.validated_data.get('check_interval')
        user.continuous_alert = self.validated_data.get('continuous_alert')
        user.save()
        return user
