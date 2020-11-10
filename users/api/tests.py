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

import pytest
from django.urls import reverse
from rest_framework.authtoken.models import Token


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
def test_logout(api_client, django_user_model):
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
    'username, email, password, password2, status_code', [
        ('', '', '', '', 400),
        ('', '', 'test-pass', 'test-pass', 400),
        ('', 'user@example.com', '', '', 400),
        ('', 'user@example.com', 'pass', 'diff_pass', 400),
        ('user', 'invalid_email.com', 'test-pass', 'test-pass', 400),
        ('user', 'user@example.com', 'test-pass', 'test-pass', 201),
    ]
)
def test_registration(username, email, password, password2, status_code, api_client):
    """
    Test user registration by providing different scenarios with the expected status_code
    """
    url = reverse('register_api')
    data = {
        'email': email,
        'username': username,
        'password': password,
        'password2': password2
    }
    response = api_client.post(url, data=data)
    assert response.status_code == status_code


@pytest.mark.django_db
def test_unauthorized_request(api_client):
    """
    Test unauthorized request, the user can't logout if he isn't logged in already
    """
    url = reverse('logout_api')
    response = api_client.post(url)
    assert response.status_code == 401
