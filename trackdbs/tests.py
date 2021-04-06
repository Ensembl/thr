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


def test_get_trackdb_without_login(api_client):
    response = api_client.get('/api/trackdb/1/')
    assert response.status_code == 401


def test_get_trackdb_success(project_dir, api_client, create_trackhub_resource):
    expected_result = {
        'owner': 'test_user',
        'created': '2021-04-06 17:28:47',
        'updated': '2021-04-06 17:28:47',
        'version': 'v1.0',
        'type': 'genomics',
        'source': {
            'checksum': None,
            'url': 'file:///' + str(project_dir) + '/' + 'samples/JASPAR_TFBS/hg19/trackDb.txt'
        },
        'hub': {
            'name': 'JASPAR_TFBS',
            'short_label': 'JASPAR TFBS',
            'long_label': 'TFBS predictions for profiles in the JASPAR CORE collections',
            'url': 'file:///' + str(project_dir) + '/' + 'samples/JASPAR_TFBS/hub.txt'
        },
        'species': {
            'scientific_name': 'Homo sapiens',
            'common_name': None,
            'taxon_id': 9606
        },
        'assembly': {
            'name': 'GRCh37',
            'accession': 'GCA_000001405.1',
            'ucsc_synonym': 'hg19'
        },
        'configuration': {}
    }

    response = api_client.get('/api/trackdb/1/')
    actual_result = response.json()
    assert response.status_code == 200
    # assert that 'owner', 'created', 'hub'.. fields are in actual_result
    assert all(k in actual_result for k in ('owner', 'created', 'hub', 'species', 'assembly', 'configuration', 'type'))


def test_get_one_trackdb_fail(api_client, create_trackhub_resource):
    expected_result = {'detail': 'Not found.'}
    response = api_client.get('/api/trackhub/144/')
    actual_result = response.json()
    assert response.status_code == 404
    assert actual_result == expected_result


@pytest.mark.parametrize(
    'trackdb_id, expected_status_code',
    [
        ('1', 204),
        ('1422', 404),
    ]
)
def test_delete_trackdb(api_client, create_trackhub_resource, trackdb_id, expected_status_code):
    response = api_client.delete('/api/trackdb/{}/'.format(trackdb_id))
    assert response.status_code == expected_status_code
