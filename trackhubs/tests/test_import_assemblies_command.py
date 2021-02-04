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

import requests
import pytest
from trackhubs.management.commands.import_assemblies import import_ena_dump
from trackhubs.models import GenomeAssemblyDump


@pytest.mark.parametrize(
    'test_url, expected_result',
    [
        ('https://www.ebi.ac.uk/ena/portal/api/search?format=json&limit=1&result=assembly', True),
        ('https://api.genome.ucsc.edu/list/ucscGenomes', True)
    ]
)
def test_request_response(test_url, expected_result):
    """
    Test whether the external ENA and UCSC's APIs server returns an OK response.
    """
    # Send a request to the API server and store the response.
    response = requests.get(test_url)
    # Confirm that the request-response cycle completed successfully.
    assert response.ok is expected_result


@pytest.mark.django_db
def test_import_ena_dump_success():
    """
    Check that genome assemblies mapping are imported successfully to the database
    """
    dumped_data_filepath = 'assemblies_dump/ena_assembly_sample.json'
    data_count = import_ena_dump(dumped_data_filepath)
    first_object = GenomeAssemblyDump.objects.first()

    assert data_count == 5
    assert first_object.accession == 'GCA_000001215'
    assert first_object.assembly_name == 'Release 5'
    assert first_object.tax_id == 7227
    assert first_object.scientific_name == 'Drosophila melanogaster'


@pytest.mark.django_db
def test_import_ena_dump_fail():
    """
    Check that genome assemblies mapping are imported successfully to the database
    """
    dumped_data_fake_filepath = 'assemblies_dump/non_existent_assembly_sample.json'
    data_count = import_ena_dump(dumped_data_fake_filepath)
    assert data_count is None
