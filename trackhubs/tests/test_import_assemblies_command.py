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

import os
import pytest
import responses

from trackhubs.management.commands.import_assemblies import import_ena_dump, fetch_assembly
from trackhubs.models import GenomeAssemblyDump


@responses.activate
def test_fetch_assembly():
    """
    Mocking fetch assembly by providing a fake API endpoint and making sure
    the JSON file 'fake_assembly' is created in 'assemblies_dump' directory
    """
    fake_url = 'http://a.fake/assembly/api'
    fake_response = {'test_message': 'This is a fake API response'}
    fake_assembly_source = 'fake'
    responses.add(responses.GET, fake_url, json=fake_response, status=404)

    json_response, _ = fetch_assembly(fake_assembly_source, fake_url)
    assert json_response == fake_response
    assert os.path.isfile('assemblies_dump/'+fake_assembly_source.lower()+'_assembly.json')


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
