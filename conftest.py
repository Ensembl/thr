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
import time

import pytest
from rest_framework.authtoken.models import Token

import trackhubs
from thr.settings import BASE_DIR


@pytest.fixture
def project_dir():
    """
    INFO: this fixture isn't used for now because it breaks CI tests
    """
    return BASE_DIR.parent


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture()
def create_user_resource(django_user_model):
    """
    Create a temporary user then return the user and token
    """
    user = django_user_model.objects.create_user(username='testuser', password='test-password', email='testuser@mail.com')
    token, _ = Token.objects.get_or_create(user=user)
    return user, token


@pytest.fixture()
def create_datatype_resource():
    """
    Create a temporary DataType object
    The created DataType will be used in various tests below
    """
    return trackhubs.models.DataType.objects.create(name='genomics')


@pytest.fixture()
def create_filetype_resource():
    return trackhubs.models.FileType.objects.create(name='bam')


@pytest.fixture()
def create_visibility_resource():
    return trackhubs.models.Visibility.objects.create(name='pack')


@pytest.fixture()
def create_species_resource():
    return trackhubs.models.Species.objects.create(taxon_id=9606, scientific_name='Homo sapiens')


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
    _, token = create_user_resource
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + str(token))
    submitted_hub = {
        # 'url': 'file:///' + str(project_dir) + '/' + 'samples/JASPAR_TFBS/hub.txt'
        'url': 'https://raw.githubusercontent.com/Ensembl/thr/master/samples/JASPAR_TFBS/hub.txt'
    }
    response = api_client.post('/api/trackhub', submitted_hub, format='json')
    return response


@pytest.fixture()
def create_hub_resource(create_user_resource, create_datatype_resource):
    """
    Create a temporary hub object
    """
    user, _ = create_user_resource
    actual_hub_obj = trackhubs.models.Hub.objects.create(
        name='JASPAR_TFBS',
        short_label='JASPAR TFBS',
        long_label='TFBS predictions for profiles in the JASPAR CORE collections',
        url='https://url/to/the/hub.txt',
        description_url='http://jaspar.genereg.net/genome-tracks/',
        email='wyeth@cmmt.ubc.ca',
        data_type=trackhubs.models.DataType.objects.filter(name=create_datatype_resource.name).first(),
        owner=user
    )
    return actual_hub_obj


@pytest.fixture()
def create_assembly_resource():
    """
    Create a temporary assembly object
    """
    actual_assembly_obj = trackhubs.models.Assembly.objects.create(
        accession='GCA_000001405.1',
        name='GRCh37',
        long_name='',
        ucsc_synonym=''
    )

    return actual_assembly_obj


@pytest.fixture()
def create_trackdb_resource(create_hub_resource, create_assembly_resource, create_species_resource):
    """
    Create a temporary trackdb object
    """
    trackdb_url = 'http://some.random/url/for/trackDb.txt'

    actual_trackdb_obj = trackhubs.models.Trackdb.objects.create(
        public=True,
        created=int(time.time()),
        updated=int(time.time()),
        assembly=create_assembly_resource,
        hub=create_hub_resource,
        species=create_species_resource,
        source_url=trackdb_url
    )
    return actual_trackdb_obj


@pytest.fixture()
def create_track_resource(create_trackdb_resource, create_filetype_resource, create_visibility_resource):
    """
    Create a temporary track object
    """
    actual_track_obj = trackhubs.models.Track.objects.create(
        # save name only without 'on' or 'off' settings
        name='JASPAR2020_TFBS_hg19',
        short_label='JASPAR2020 TFBS hg19',
        long_label='TFBS predictions for all profiles in the JASPAR CORE vertebrates collection (2020)',
        big_data_url='http://path.to/the/track/bigbed/file/JASPAR2020_hg19.bb',
        parent=None,
        trackdb=create_trackdb_resource,
        file_type=trackhubs.models.FileType.objects.filter(name='bam').first(),
        visibility=trackhubs.models.Visibility.objects.filter(name='pack').first()
    )
    return actual_track_obj


@pytest.fixture()
def create_child_track_resource(create_trackdb_resource, create_filetype_resource, create_visibility_resource,
                                create_track_resource):
    """
    Create a temporary track object which is the child of another track
    this parent track is empty, it is used to test add_parent_id() function
    """
    actual_track_obj = trackhubs.models.Track.objects.create(
        # save name only without 'on' or 'off' settings
        name='Child track name',
        short_label='child of JASPAR2020',
        long_label='This is the child of the track described as follows: TFBS predictions for all profiles in the '
                   'JASPAR CORE vertebrates collection (2020)',
        big_data_url='http://path.to/the/subtrack/bigbed/file/JASPAR2020_hg19_subtrack.bb',
        parent=None,
        trackdb=create_trackdb_resource,
        file_type=trackhubs.models.FileType.objects.filter(name='bam').first(),
        visibility=trackhubs.models.Visibility.objects.filter(name='pack').first()
    )
    return actual_track_obj


@pytest.fixture()
def create_child_track_with_parent_resource(create_trackdb_resource, create_filetype_resource,
                                            create_visibility_resource, create_track_resource):
    """
    Create a temporary track object which is the child of another track
    this parent track is provided, it is used to test get_parents() function
    """
    actual_track_obj = trackhubs.models.Track.objects.create(
        # save name only without 'on' or 'off' settings
        name='Child track name',
        short_label='child of JASPAR2020',
        long_label='This is the child of the track described as follows: TFBS predictions for all profiles in the '
                   'JASPAR CORE vertebrates collection (2020)',
        big_data_url='http://path.to/the/subtrack/bigbed/file/JASPAR2020_hg19_subtrack.bb',
        parent=create_track_resource,
        trackdb=create_trackdb_resource,
        file_type=trackhubs.models.FileType.objects.filter(name='bam').first(),
        visibility=trackhubs.models.Visibility.objects.filter(name='pack').first()
    )
    return actual_track_obj
