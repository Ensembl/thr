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


@pytest.mark.django_db
def test_summary_stats(api_client, create_hub_resource, create_species_resource, create_assembly_resource):
    expected_result = [
        ['Element', '', {'role': 'style'}],
        ['Hubs', 1, 'color: gray'],
        ['Species', 1, 'color: #76A7FA'],
        ['Assemblies', 1, 'opacity: 0.2']
    ]
    response = api_client.get('/api/stats/summary')
    actual_result = response.json()
    assert response.status_code == 200
    assert actual_result == expected_result


@pytest.mark.django_db
def test_complete_stats(api_client, create_track_resource):
    expected_result = {
        'hubs_per_species': {'Homo sapiens': 1},
        'hubs_per_assemblies': {'GRCh37': 1},
        'hubs_per_file_type': {'bam': 1},
        'species_per_file_type': {'bam': 1},
        'assemblies_per_file_type': {'bam': 1},
        'tracks_per_file_type': {'bam': 1}
    }
    response = api_client.get('/api/stats/complete')
    actual_result = response.json()
    assert response.status_code == 200
    assert actual_result == expected_result
