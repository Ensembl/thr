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
from rest_framework.authtoken.models import Token


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture()
def create_user_resource(django_user_model):
    """
    Create a temporary user and return the token
    """
    user = django_user_model.objects.create_user(username='test_user', password='test-password')
    token, _ = Token.objects.get_or_create(user=user)
    return token


@pytest.fixture()
def create_trackhub_resource(api_client, create_user_resource):
    """
    This fixture is used to create a temporary trackhub using POST API
    The created trackhub will be used to test GET API
    """
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + create_user_resource.key)
    submitted_hub = {
        "url": "https://raw.githubusercontent.com/Ensembl/thr/feat/add_elasticsearch/samples/JASPAR_TFBS/hub.txt"
    }
    response = api_client.post('/api/trackhub/', submitted_hub, format='json')
    return response


def test_post_trackhub_success(api_client, create_user_resource):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + create_user_resource.key)
    submitted_hub = {
        "url": "https://raw.githubusercontent.com/Ensembl/thr/feat/add_elasticsearch/samples/JASPAR_TFBS/hub.txt",
        "assemblies": {
            "assembly1": "assembly1_value",
            "assembly2": "assembly2_value"
        },
        "type": "genomics"
    }
    response = api_client.post('/api/trackhub/', submitted_hub, format='json')
    # print("## Response message: {}".format(response.content.decode()))
    assert response.status_code == 201


def test_post_trackhub_bad_url(api_client, create_user_resource):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + create_user_resource.key)
    submitted_hub = {
        "url": "https://some.random/bad/url/hub.txt"
    }
    response = api_client.post('/api/trackhub/', submitted_hub, format='json')
    assert response.status_code == 400


def test_post_trackhub_no_url_field(api_client, create_user_resource):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + create_user_resource.key)
    submitted_hub = {
        "wrong_field_name": "https://raw.githubusercontent.com/Ensembl/thr/feat/add_elasticsearch/samples/JASPAR_TFBS/hub.txt"
    }
    response = api_client.post('/api/trackhub/', submitted_hub, format='json')
    assert response.status_code == 400


def test_post_trackhub_without_login(api_client):
    submitted_hub = {
        "url": "https://raw.githubusercontent.com/Ensembl/thr/feat/add_elasticsearch/samples/JASPAR_TFBS/hub.txt"
    }
    response = api_client.post('/api/trackhub/', submitted_hub, format='json')
    assert response.status_code == 401


def test_get_trackhub_without_login(api_client):
    response = api_client.get('/api/trackhub/')
    assert response.status_code == 401


# TODO: This test causes an error, I'll look into it
# def test_get_trackhub_success(api_client, create_trackhub_resource):
#     expected_result = [{
#         "hub_id": 1,
#         "name": "JASPAR_TFBS",
#         "short_label": "JASPAR TFBS",
#         "long_label": "TFBS predictions for profiles in the JASPAR CORE collections",
#         "url": "https://raw.githubusercontent.com/Ensembl/thr/feat/add_elasticsearch/samples/JASPAR_TFBS/hub.txt",
#         "description_url": "http://jaspar.genereg.net/genome-tracks/",
#         "email": "wyeth@cmmt.ubc.ca"
#     }]
#
#     response = api_client.get('/api/trackhub/')
#     actual_result = response.json()
#     assert response.status_code == 200
#     assert actual_result == expected_result
