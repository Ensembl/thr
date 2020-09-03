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
import uuid

import pytest
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_user_create():
    User.objects.create_user('user1', 'user@mail.com', 'userpassword')
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_superuser_create():
    user = User.objects.create_user('superuser1', 'superuser@mail.com', 'superuserpassword', is_superuser=True)
    assert user.is_superuser


@pytest.mark.django_db
def test_view(client):
    url = reverse('thr-home')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_unauthorized(client):
    url = reverse('dashboard')
    response = client.get(url)
    # 302 Found and redirect to login
    assert response.status_code == 302


@pytest.mark.django_db
def test_superuser_view(admin_client):
    url = reverse('dashboard')
    response = admin_client.get(url)
    assert response.status_code == 200


@pytest.fixture
def test_password():
    return 'strong-test-pass'


@pytest.fixture
def create_user(db, django_user_model, test_password):
    def make_user(**kwargs):
        kwargs['password'] = test_password
        if 'username' not in kwargs:
            kwargs['username'] = str(uuid.uuid4())
        return django_user_model.objects.create_user(**kwargs)

    return make_user


@pytest.fixture
def auto_login_user(db, client, create_user, test_password):
    def make_auto_login(user=None):
        if user is None:
            user = create_user()
        client.login(username=user.username, password=test_password)
        return client, user

    return make_auto_login


@pytest.mark.django_db
def test_auth_view(auto_login_user):
    client, user = auto_login_user()
    url = reverse('login')
    response = client.get(url)
    assert response.status_code == 200

