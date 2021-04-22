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


@pytest.mark.parametrize(
    'query_body, expected_total_hits',
    [
        # ({"query": "Homo sapiens"}, 19),
        # ({"query": "Homo sapiens", "accession": "GCA_000001405.1"}, 3),
        ({"query": "Homo sapiens", "accession": "GCA_000001405.1", "species": "Homo sapiens", "hub": "JASPAR_TFBS"}, 2),
        ({"query": "Homo sapiens", "accession": "GCA_000001405.1", "species": "Homo sapiens", "hub": "JASPAR_TFBS", "assembly": "GRCh37"}, 2),
    ]
)
def test_post_search_success(api_client, query_body, expected_total_hits):
    response = api_client.post('/api/search/', query_body, format='json')
    actual_total_hits = response.json()['hits']['total']

    assert actual_total_hits == expected_total_hits
    assert response.status_code == 200


@pytest.mark.parametrize(
    'query_body, expected_error_message',
    [
        ({"query": ""}, {'error': 'Missing query field'}),
        ({"random_name": "Homo sapiens"}, {'error': 'Missing query field'}),
        ({"random_name": "Homo sapiens", "accession": "GCA_000001405.1", "species": "Homo sapiens", "hub": "JASPAR_TFBS"}, {'error': 'Missing query field'}),
        ({}, {'error': 'Missing message body in request'}),
    ]
)
def test_post_search_fail(api_client, query_body, expected_error_message):
    response = api_client.post('/api/search/', query_body, format='json')
    actual_error_message = response.json()
    assert actual_error_message == expected_error_message
    assert response.status_code == 400


def test_get_one_trackdb_success(api_client):
    response = api_client.get('/api/search/trackdb/1/')
    actual_result = response.json()
    assert actual_result['id'] == '1'
    assert response.status_code == 200


def test_get_one_trackdb_fail(api_client):
    expected_result = {'error': 'TrackDB document not found.'}
    response = api_client.get('/api/search/trackdb/144/')
    actual_result = response.json()
    assert response.status_code == 404
    assert actual_result == expected_result
