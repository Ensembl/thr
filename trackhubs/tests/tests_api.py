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


def test_post_trackhub_success(project_dir, api_client, create_user_resource, create_genome_assembly_dump_resource):
    _, token = create_user_resource
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + str(token))
    submitted_hub = {
        # 'url': 'file:///' + str(project_dir) + '/' + 'samples/JASPAR_TFBS/hub.txt',
        'url': 'https://raw.githubusercontent.com/Ensembl/thr/master/samples/JASPAR_TFBS/hub.txt',
        'assemblies': {
            'assembly1': 'assembly1_value',
            'assembly2': 'assembly2_value'
        },
        'type': 'genomics'
    }
    response = api_client.post('/api/trackhub/', submitted_hub, format='json')
    # print("## Response message: {}".format(response.content.decode()))
    assert response.status_code == 201


def test_post_trackhub_bad_url(api_client, create_user_resource):
    _, token = create_user_resource
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + str(token))
    submitted_hub = {
        'url': 'https://some.random/bad/url/hub.txt'
    }
    response = api_client.post('/api/trackhub/', submitted_hub, format='json')
    assert response.status_code == 400


def test_post_trackhub_no_url_field(project_dir, api_client, create_user_resource):
    _, token = create_user_resource
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + str(token))
    submitted_hub = {
        # 'wrong_field_name': 'file:///' + str(project_dir) + '/' + 'samples/JASPAR_TFBS/hub.txt'
        'wrong_field_name': 'https://raw.githubusercontent.com/Ensembl/thr/master/samples/JASPAR_TFBS/hub.txt'
    }
    response = api_client.post('/api/trackhub/', submitted_hub, format='json')
    assert response.status_code == 400


def test_post_trackhub_without_login(project_dir, api_client):
    submitted_hub = {
        # 'url': 'file:///' + str(project_dir) + '/' + 'samples/JASPAR_TFBS/hub.txt'
        'url': 'https://raw.githubusercontent.com/Ensembl/thr/master/samples/JASPAR_TFBS/hub.txt'
    }
    response = api_client.post('/api/trackhub/', submitted_hub, format='json')
    assert response.status_code == 401


def test_get_trackhub_without_login(api_client):
    response = api_client.get('/api/trackhub/')
    assert response.status_code == 401


def test_get_trackhub_success(project_dir, api_client, create_trackhub_resource):
    expected_result = [{
        'hub_id': 1,
        'name': 'JASPAR_TFBS',
        'short_label': 'JASPAR TFBS',
        'long_label': 'TFBS predictions for profiles in the JASPAR CORE collections',
        # 'url': 'file:///' + str(project_dir) + '/' + 'samples/JASPAR_TFBS/hub.txt',
        'url': 'https://raw.githubusercontent.com/Ensembl/thr/master/samples/JASPAR_TFBS/hub.txt',
        'description_url': 'http://jaspar.genereg.net/genome-tracks/',
        'email': 'wyeth@cmmt.ubc.ca',
        'trackdbs': [
            {
                'trackdb_id': 1,
                'species': 'TODO: Link species to Trackdb instead of Hub',
                'assembly': 'GRCh37',
                'uri': 'https://www.new-trackhubregistry-url.org/user/view_trackhub_status/1',
                'schema': 'v1.0',
                'created': 'the date changes',
                'updated': 'the date changes'
            },
            {
                'trackdb_id': 2,
                'species': 'TODO: Link species to Trackdb instead of Hub',
                'assembly': 'GRCh38',
                'uri': 'https://www.new-trackhubregistry-url.org/user/view_trackhub_status/2',
                'schema': 'v1.0',
                'created': 'the date changes',
                'updated': 'the date changes'
            }]
    }]

    response = api_client.get('/api/trackhub/')
    actual_result = response.json()
    assert response.status_code == 200
    assert actual_result[0]['hub_id'] == expected_result[0]['hub_id']
    assert actual_result[0]['name'] == expected_result[0]['name']
    assert actual_result[0]['url'] == expected_result[0]['url']
    assert len(actual_result[0]['trackdbs']) == len(expected_result[0]['trackdbs'])


def test_get_one_trackhub_success(project_dir, api_client, create_trackhub_resource):
    expected_result = {
        'hub_id': 1,
        'name': 'JASPAR_TFBS',
        'short_label': 'JASPAR TFBS',
        'long_label': 'TFBS predictions for profiles in the JASPAR CORE collections',
        # 'url': 'file:///' + str(project_dir) + '/' + 'samples/JASPAR_TFBS/hub.txt',
        'url': 'https://raw.githubusercontent.com/Ensembl/thr/master/samples/JASPAR_TFBS/trackDb.txt',
        'description_url': 'http://jaspar.genereg.net/genome-tracks/',
        'email': 'wyeth@cmmt.ubc.ca',
        'trackdbs': [
            {
                'trackdb_id': 1,
                'species': {
                    'TODO': 'Link species to Trackdb instead of Hub'
                },
                'assembly': {
                    'name': 'GRCh37',
                    'long_name': 'GRCh37',
                    'accession': 'GCA_000001405.1',
                    'synonyms': 'hg19'
                },
                'uri': 'https://www.new-trackhubregistry-url.org/user/view_trackhub_status/1'
            },
            {
                'trackdb_id': 2,
                'species': {
                    'TODO': 'Link species to Trackdb instead of Hub'
                },
                'assembly': {
                    'name': 'GRCh38',
                    'long_name': 'GRCh38',
                    'accession': 'GCA_000001405.15',
                    'synonyms': 'hg38'
                },
                'uri': 'https://www.new-trackhubregistry-url.org/user/view_trackhub_status/2'
            }
        ]
    }

    response = api_client.get('/api/trackhub/1/')
    actual_result = response.json()
    assert response.status_code == 200
    # assert actual_result['hub_id'] == expected_result['hub_id']
    assert actual_result['name'] == expected_result['name']
    assert actual_result['url'] == expected_result['url']
    assert len(actual_result['trackdbs']) == len(expected_result['trackdbs'])


def test_get_one_trackhub_fail(api_client, create_trackhub_resource):
    expected_result = {'detail': 'Not found.'}
    response = api_client.get('/api/trackhub/144/')
    actual_result = response.json()
    assert response.status_code == 404
    assert actual_result == expected_result


@pytest.mark.parametrize(
    'hub_id, expected_status_code',
    [
        ('1', 204),
        ('144', 404),
    ]
)
def test_delete_trackhub(api_client, create_trackhub_resource, hub_id, expected_status_code):
    response = api_client.delete('/api/trackhub/{}/'.format(hub_id))
    assert response.status_code == expected_status_code
