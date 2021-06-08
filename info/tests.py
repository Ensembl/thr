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


def test_version(api_client):
    expected_result = {'version': 0.01}
    response = api_client.get('/api/info/version')
    actual_result = response.json()
    assert response.status_code == 200
    assert actual_result == expected_result


def test_ping(api_client):
    expected_result = {'ping': 1}
    response = api_client.get('/api/info/ping')
    actual_result = response.json()
    assert response.status_code == 200
    assert actual_result == expected_result


@pytest.mark.django_db
def test_species_info(api_client, create_species_resource):
    expected_result = ['Homo sapiens']
    response = api_client.get('/api/info/species')
    actual_result = response.json()
    assert response.status_code == 200
    assert actual_result == expected_result


@pytest.mark.django_db
def test_assemblies_info(api_client, create_trackhub_resource):
    expected_result = {
        'Homo sapiens': [
            {
                'name': 'GRCh37',
                'accession': 'GCA_000001405.1',
                'synonyms': [
                    'hg19'
                ]
            },
            {
                'name': 'GRCh38',
                'accession': 'GCA_000001405.15',
                'synonyms': [
                    'hg38'
                ]
            },
        ]
    }
    response = api_client.get('/api/info/assemblies')
    actual_result = response.json()
    assert response.status_code == 200
    assert actual_result == expected_result


@pytest.mark.parametrize(
    'assembly, expected_result',
    [
        ('GRCh38', {'tot': 1}),
        ('GCA_000001405.15', {'tot': 1}),
    ]
)
@pytest.mark.django_db
def test_hub_per_assembly_info(api_client, assembly, expected_result, create_trackhub_resource):
    response = api_client.get('/api/info/hubs_per_assembly/' + assembly)
    actual_result = response.json()
    # print('actual_result ---> ', actual_result)
    assert response.status_code == 200
    assert actual_result == expected_result


@pytest.mark.parametrize(
    'assembly, expected_result',
    [
        ('GRCh38', {'tot': 2}),
        ('GCA_000001405.15', {'tot': 2}),
    ]
)
@pytest.mark.django_db
def test_tracks_per_assembly_info(api_client, assembly, expected_result, create_trackhub_resource):
    response = api_client.get('/api/info/tracks_per_assembly/' + assembly)
    actual_result = response.json()
    assert response.status_code == 200
    assert actual_result == expected_result


@pytest.mark.django_db
def test_trackhubs_info(project_dir, api_client, create_trackhub_resource):
    expected_result = {
        'name': 'JASPAR_TFBS',
        'shortLabel': 'JASPAR TFBS',
        'longLabel': 'TFBS predictions for profiles in the JASPAR CORE collections',
        'url': 'file:///' + str(project_dir) + '/' + 'samples/JASPAR_TFBS/hub.txt',
        'trackdbs': [
            {
                'species': '9606',
                'uri': 'https://www.trackhubregistry.org/api/search/trackdb/1',
                'assembly': 'GCA_000001405.1'
            },
            {
                'species': '9606',
                'uri': 'https://www.trackhubregistry.org/api/search/trackdb/2',
                'assembly': 'GCA_000001405.15'
            }
        ]
    }
    response = api_client.get('/api/info/trackhubs')
    actual_result = response.json()
    assert response.status_code == 200
    assert actual_result == expected_result
