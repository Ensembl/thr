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

import trackhubs
from thr.settings import BASE_DIR


@pytest.fixture
def project_dir():
    return BASE_DIR.parent


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture()
def create_user_resource(django_user_model):
    """
    Create a temporary user and return the token
    """
    user = django_user_model.objects.create_user(username='test_user', password='test_password')
    token, _ = Token.objects.get_or_create(user=user)
    return token


@pytest.fixture()
def create_genome_assembly_dump_resource():
    hg19_dump = trackhubs.models.GenomeAssemblyDump(
        accession='GCA_000001405',
        version=1,
        accession_with_version='GCA_000001405.1',
        assembly_name='GRCh37',
        assembly_title='Genome Reference Consortium Human Build 37 (GRCh37)',
        tax_id=9606,
        scientific_name='Homo sapiens',
        ucsc_synonym='hg19',
        api_last_updated='2013-08-08'
    )
    hg38_dump = trackhubs.models.GenomeAssemblyDump(
        accession='GCA_000001405',
        version=15,
        accession_with_version='GCA_000001405.15',
        assembly_name='GRCh38',
        assembly_title='Genome Reference Consortium Human Build 38',
        tax_id=9606,
        scientific_name='Homo sapiens',
        ucsc_synonym='hg38',
        api_last_updated='2019-02-28'
    )
    return trackhubs.models.GenomeAssemblyDump.objects.bulk_create([hg19_dump, hg38_dump])


@pytest.fixture()
def create_trackhub_resource(project_dir, api_client, create_user_resource, create_genome_assembly_dump_resource):
    """
    This fixture is used to create a temporary trackhub using POST API
    The created trackhub will be used to test GET API
    """
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + create_user_resource.key)
    submitted_hub = {
        'url': 'file:///' + str(project_dir) + '/' + 'samples/JASPAR_TFBS/hub.txt'
    }
    response = api_client.post('/api/trackhub/', submitted_hub, format='json')
    return response
