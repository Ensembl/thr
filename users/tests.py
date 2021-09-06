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
import re

import django
import pytest
from django.urls import reverse
from rest_framework.authtoken.models import Token
from users.models import CustomUser as User


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.mark.django_db
def test_login_success(api_client, django_user_model):
    """
    Test user login
    :param api_client: the API client
    :param django_user_model: a shortcut to the User model configured for use by the
    current Django project
    """
    username = 'user'
    password = 'password'
    django_user_model.objects.create_user(username=username, password=password)
    url = reverse('login_api')
    data = {
        'username': username,
        'password': password
    }
    response = api_client.post(url, data=data)
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize(
    'username, password, status_code', [
        ('', '', 400),
        ('', 'pass', 400),
        ('non_existing_user', 'pass', 400),
    ]
)
@pytest.mark.django_db
def test_login_fail(username, password, status_code, api_client):
    """
    Test user login failure when the provided credential aren't correct
    """
    url = reverse('login_api')
    data = {
        'username': username,
        'password': password
    }
    response = api_client.post(url, data=data)
    assert response.status_code == status_code


@pytest.mark.django_db
def test_logout_success(api_client, django_user_model):
    """
    Log the user in and out while providing the access token
    """
    user = django_user_model.objects.create_user(username='user', password='password')
    token, _ = Token.objects.get_or_create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    url = reverse('logout_api')
    response = api_client.post(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_logout_fail(api_client):
    """
    Log the user in and out while providing the access token
    """
    token = 'random14token77definitely895invalid'
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    url = reverse('logout_api')
    response = api_client.post(url)
    assert response.status_code == 401


@pytest.mark.django_db
@pytest.mark.parametrize(
    'data, status_code', [
        ({'email': '', 'username': '', 'password': '', 'password2': '', 'check_interval': ''}, 400),
        ({'email': '', 'username': '', 'password': 'test-pass', 'password2': 'test-pass', 'check_interval': ''}, 400),
        ({'email': 'user@example.com', 'username': '', 'password': '', 'password2': '', 'check_interval': ''}, 400),
        ({'email': 'user@example.com', 'username': '', 'password': 'pass', 'password2': 'diff_pass', 'check_interval': ''}, 400),
        ({'email': 'invalid_email.com', 'username': 'user', 'password': 'test-pass', 'password2': 'test-pass', 'check_interval': ''}, 400),
        ({'email': 'invalid_email.com', 'username': 'user', 'password': 'test-pass', 'password2': 'test-pass', 'check_interval': ''}, 400),
        ({'email': 'user@example.com', 'username': 'user', 'password': 'test-pass', 'password2': 'test-pass', 'check_interval': 'automatic'}, 201),
    ]
)
def test_registration(api_client, data, status_code):
    """
    Test user registration by providing different scenarios with the expected status_code
    """
    url = reverse('register_api')
    response = api_client.post(url, data)
    assert response.status_code == status_code


@pytest.mark.django_db
def test_email_verification_success(api_client):
    """
    Test email verification
    """
    payload = {
        'email': 'user@example.com',
        'username': 'user',
        'password': 'test-pass',
        'password2': 'test-pass',
        'check_interval': 'automatic'
    }

    registration_url = reverse('register_api')
    registration_response = api_client.post(registration_url, payload)
    # assert that the user is registered successfully
    assert registration_response.status_code == 201

    # get the new registered user
    user = User.objects.get(email=payload['email'])
    # and make sure the account is not activated
    assert user.is_active is False

    # get token from email
    # use a regex to match the expected link
    token_regex = r"email_verification\?token=([A-Za-z0-9:\-._]+)"
    email_content = django.core.mail.outbox[0].body
    # search for the pattern in the email
    match = re.search(token_regex, email_content)
    assert match.groups()
    token = match.group(1)

    # verify that the token we got is working
    email_verification_response = api_client.get('/api/email_verification?token=' + token)
    actual_result = email_verification_response.json()
    assert email_verification_response.status_code == 200
    assert actual_result == {'success': 'Account successfully activated!'}


@pytest.mark.django_db
def test_email_verification_fail(api_client):
    """
    Test email verification using the wrong token
    """
    payload = {
        'email': 'user@example.com',
        'username': 'user',
        'password': 'test-pass',
        'password2': 'test-pass',
        'check_interval': 'automatic'
    }

    registration_url = reverse('register_api')
    registration_response = api_client.post(registration_url, payload)
    # assert that the user is registered successfully
    assert registration_response.status_code == 201

    # create random token
    token = 'eyJ0eXAiOiJKV1jo.YWNjZXNzIiwiZXhw.oxNjMwOTQ4OTg3LCJqdGkiOiJmY2ZhNzQ3ZjQ1OGJfaWQiOjF9_otTBItQfC7aozK_VgWcY'

    # verify that the token we created isn't working
    email_verification_response = api_client.get('/api/email_verification?token=' + token)
    actual_result = email_verification_response.json()
    assert email_verification_response.status_code == 400
    assert actual_result == {'error': 'Invalid token'}


@pytest.mark.django_db
def test_unauthorized_request(api_client):
    """
    Test unauthorized request, the user can't logout if he isn't logged in already
    """
    url = reverse('logout_api')
    response = api_client.post(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_get_user_details_success(api_client, django_user_model):
    """
    List the user details after providing the access token
    """
    user = django_user_model.objects.create_user(username='user', password='password')
    token, _ = Token.objects.get_or_create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    url = reverse('user_api')
    response = api_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_user_details_fail(api_client, django_user_model):
    """
    List the user details after providing the access token
    """
    token = 'another455random14token77definitely895invalid'
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    url = reverse('user_api')
    response = api_client.get(url)
    assert response.status_code == 401


@pytest.mark.django_db
@pytest.mark.parametrize(
    'data, expected_result, expected_status_code', [
        (
            {},
            {'error': 'Missing message body in request'},
            400
        ),
        (
            {'foo': 'user', 'bar': 'user'},
            {'email': ['This field is required.'], 'check_interval': ['This field is required.']},
            400
        ),
        (
            {'email': 'invalid_email'},
            {'email': ['Enter a valid email address.'], 'check_interval': ['This field is required.']},
            400
        ),
        (
            {'email': 'user@mail.com'},
            {'check_interval': ['This field is required.']},
            400
        ),
        (
            {'email': 'user@mail.com', 'check_interval': 'foo'},
            {'check_interval': ['"foo" is not a valid choice.']},
            400
        ),
        (
            {'check_interval': 'automatic'},
            {'email': ['This field is required.']},
            400
        ),
        (
            {'email': 'user@mail.com', 'check_interval': 'weekly', 'continuous_alert': 'foo'},
            {'continuous_alert': ['Must be a valid boolean.']},
            400
        ),
        (
            {
                'email': 'usr@mail.com',
                'first_name': 'First',
                'last_name': 'User',
                'affiliation': 'EBI',
                'check_interval': 'monthly',
                'continuous_alert': 'false',
            },
            {'success': 'User profile updated successfully!'},
            200
        ),
    ]
)
def test_post_user_details(api_client, django_user_model, data, expected_result, expected_status_code):
    """
    Edit the user details after providing the access token
    """
    user = django_user_model.objects.create_user(username='user', password='password')
    token, _ = Token.objects.get_or_create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    url = reverse('user_api')
    response = api_client.post(url, data)
    actual_result = response.json()
    assert actual_result == expected_result
    assert response.status_code == expected_status_code


def test_change_user_password_success(api_client, django_user_model):
    """
    Change the user password after providing the old one
    """
    user = django_user_model.objects.create_user(username='user', password='old_pass')
    token, _ = Token.objects.get_or_create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    url = reverse('change_password_api')
    data = {'old_password': 'old_pass', 'new_password1': 'new_pass', 'new_password2': 'new_pass'}
    response = api_client.put(url, data)
    # e.g: {'success': 'Your password is updated successfully!', 'token': 'd57a4e7987944e5cb87659512d751b4241132fcb'}
    assert 'success' in response.json()
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize(
    'data, expected_result, expected_status_code', [
        (
            {'useless': 'info'},
            {
                'old_password': ['This field is required.'],
                'new_password1': ['This field is required.'],
                'new_password2': ['This field is required.']
            },
            400
        ),
        (
            {'old_password': 'foo'},
            {
                'old_password': ['Your old password was entered incorrectly. Please enter it again.'],
                'new_password1': ['This field is required.'],
                'new_password2': ['This field is required.']
            },
            400
        ),
        (
            {'old_password': 'old_pass'},
            {'new_password1': ['This field is required.'], 'new_password2': ['This field is required.']},
            400
        ),
        (
            {'old_password': 'old_pass', 'new_password1': 'new_pass'},
            {'new_password2': ['This field is required.']},
            400
        ),
        (
            {'old_password': 'old_pass', 'new_password1': 'new_pass', 'new_password2': 'new_pass_ops'},
            {'error': ["The two password fields didn't match."]},
            400
        ),
        (
            {'old_password': 'old_pass', 'new_password1': 'new_pass', 'new_password2': 'new_pass_mismatch'},
            {'error': ["The two password fields didn't match."]},
            400
        ),
    ]
)
def test_change_user_password_fail(api_client, django_user_model, data, expected_result, expected_status_code):
    """
    Change the user password after providing the old one
    """
    user = django_user_model.objects.create_user(username='user', password='old_pass')
    token, _ = Token.objects.get_or_create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    url = reverse('change_password_api')
    response = api_client.put(url, data)
    actual_result = response.json()
    assert actual_result == expected_result
    assert response.status_code == expected_status_code
