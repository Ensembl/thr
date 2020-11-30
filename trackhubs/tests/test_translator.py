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
from trackhubs.constants import FILE_TYPES, DATA_TYPES, VISIBILITY
from trackhubs import translator, models


@pytest.fixture
def project_dir():
    return BASE_DIR.parent


@pytest.fixture()
def create_user_resource(django_user_model):
    """
    Create a temporary user then return the user and token
    """
    user = django_user_model.objects.create_user(username='test_user', password='test-password')
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
def create_hub_resource(create_user_resource, create_datatype_resource, create_species_resource):
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
        species=create_species_resource,
        owner=user
    )
    return actual_hub_obj


@pytest.fixture()
def create_genome_resource(create_hub_resource):
    """
    Create a temporary genome object
    """
    actual_genome_obj = trackhubs.models.Genome.objects.create(
        name='hg19',
        trackdb_location='hg19/trackDb.txt',
        hub=create_hub_resource
    )
    return actual_genome_obj


@pytest.fixture()
def create_assembly_resource(create_genome_resource):
    """
    Create a temporary assembly object
    """
    actual_assembly_obj = trackhubs.models.Assembly.objects.create(
        accession='GCA_000001405.1',
        name='GRCh37',
        long_name='',
        synonyms='',
        genome=create_genome_resource
    )

    return actual_assembly_obj


@pytest.fixture()
def create_trackdb_resource(create_hub_resource, create_genome_resource, create_assembly_resource):
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
        genome=create_genome_resource,
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


@pytest.mark.django_db
def test_save_datatype_filetype_visibility():
    trackhubs.translator.save_datatype_filetype_visibility(DATA_TYPES, trackhubs.models.DataType)
    trackhubs.translator.save_datatype_filetype_visibility(FILE_TYPES, trackhubs.models.FileType)
    trackhubs.translator.save_datatype_filetype_visibility(VISIBILITY, trackhubs.models.Visibility)

    saved_datatypes_count = trackhubs.models.DataType.objects.all().count()
    saved_filetypes_count = trackhubs.models.FileType.objects.all().count()
    saved_visibilities_count = trackhubs.models.Visibility.objects.all().count()

    assert saved_datatypes_count == len(DATA_TYPES)
    assert saved_filetypes_count == len(FILE_TYPES)
    assert saved_visibilities_count == len(VISIBILITY)


@pytest.mark.django_db
def test_get_datatype_filetype_visibility():
    actual_datatype_obj = trackhubs.models.DataType.objects.create(name='genomics')
    expected_datatype_obj = trackhubs.translator.get_datatype_filetype_visibility('genomics', trackhubs.models.DataType)
    assert actual_datatype_obj == expected_datatype_obj

    actual_filetype_obj = trackhubs.models.FileType.objects.create(name='bam')
    expected_filetype_obj = trackhubs.translator.get_datatype_filetype_visibility('bam', trackhubs.models.FileType)
    assert actual_filetype_obj == expected_filetype_obj

    actual_visibility_obj = trackhubs.models.Visibility.objects.create(name='hide')
    expected_visibility_obj = trackhubs.translator.get_datatype_filetype_visibility('hide', trackhubs.models.Visibility)
    assert actual_visibility_obj == expected_visibility_obj


@pytest.mark.django_db
def test_save_hub(create_hub_resource):
    expected_hub_info = {
        'hub': 'JASPAR_TFBS',
        'shortLabel': 'JASPAR TFBS',
        'longLabel': 'TFBS predictions for profiles in the JASPAR CORE collections',
        'genomesFile': 'genomes.txt',
        'email': 'wyeth@cmmt.ubc.ca',
        'descriptionUrl': 'http://jaspar.genereg.net/genome-tracks/',
        'url': 'https://url/to/the/hub.txt'
    }

    assert expected_hub_info['hub'] == create_hub_resource.name
    assert expected_hub_info['shortLabel'] == create_hub_resource.short_label
    assert expected_hub_info['longLabel'] == create_hub_resource.long_label
    assert expected_hub_info['email'] == create_hub_resource.email
    assert expected_hub_info['descriptionUrl'] == create_hub_resource.description_url
    assert expected_hub_info['url'] == create_hub_resource.url


@pytest.mark.django_db
def test_save_genome(create_genome_resource):
    expected_genome_info = {
        'genome': 'hg19',
        'trackDb': 'hg19/trackDb.txt',
        'url': 'https://url/to/the/genomes.txt'
    }

    assert expected_genome_info['genome'] == create_genome_resource.name
    assert expected_genome_info['trackDb'] == create_genome_resource.trackdb_location


@pytest.mark.django_db
def test_save_assembly(create_assembly_resource):
    expected_assembly_info = {
        'accession': 'GCA_000001405.1',
        'name': 'GRCh37'
    }

    assert expected_assembly_info['accession'] == create_assembly_resource.accession
    assert expected_assembly_info['name'] == create_assembly_resource.name


@pytest.mark.django_db
def test_save_trackdb(create_trackdb_resource):
    expected_trackdb_info = {
        'public': True,
        'source_url': 'http://some.random/url/for/trackDb.txt'
    }

    assert expected_trackdb_info['public'] == create_trackdb_resource.public
    assert expected_trackdb_info['source_url'] == create_trackdb_resource.source_url


@pytest.mark.django_db
def test_save_track(create_track_resource):
    expected_track_info = {
        'track': 'JASPAR2020_TFBS_hg19',
        'shortLabel': 'JASPAR2020 TFBS hg19',
        'longLabel': 'TFBS predictions for all profiles in the JASPAR CORE vertebrates collection (2020)',
        'type': 'bigBed 6 +',
        'bigDataUrl': 'http://path.to/the/track/bigbed/file/JASPAR2020_hg19.bb'
    }

    assert expected_track_info['track'] == create_track_resource.name
    assert expected_track_info['shortLabel'] == create_track_resource.short_label
    assert expected_track_info['longLabel'] == create_track_resource.long_label
    assert expected_track_info['bigDataUrl'] == create_track_resource.big_data_url


@pytest.mark.parametrize(
    'string_with_spaces, expected_result',
    [
        ('bigBed 6 +', 'bigBed'),  # space
        ('bigBed    6 +', 'bigBed'),  # tab
    ]
)
def test_get_first_word(string_with_spaces, expected_result):
    actual_result = trackhubs.translator.get_first_word(string_with_spaces)
    assert expected_result == actual_result


@pytest.mark.django_db
def test_add_parent_id(create_track_resource, create_child_track_resource):
    parent_name = 'JASPAR2020_TFBS_hg19 off'
    parent_track = trackhubs.translator.add_parent_id(
        parent_name=parent_name,
        current_track=create_child_track_resource
    )
    # assert that the added parent id is actually the parent id
    assert parent_track.track_id == create_child_track_resource.parent_id


@pytest.mark.django_db
def test_get_parents(create_child_track_with_parent_resource):
    parent_track, grandparent_track = trackhubs.translator.get_parents(create_child_track_with_parent_resource)
    assert parent_track.track_id == create_child_track_with_parent_resource.parent_id
    assert grandparent_track is None


@pytest.mark.parametrize(
    'hub_url, expected_result',
    [
        ('https://url/to/the/hub.txt', True),
        ('https://url/to/non/existing/hub.txt', False),
    ]
)
@pytest.mark.django_db
def test_is_hub_exists(hub_url, expected_result, create_hub_resource):
    actual_result = trackhubs.translator.is_hub_exists(hub_url)
    assert actual_result == expected_result


@pytest.mark.django_db
def test_save_and_update_document_success(project_dir, create_user_resource):
    user, _ = create_user_resource

    fake_hub_url = 'file:///' + str(project_dir) + '/' + 'samples/JASPAR_TFBS/hub.txt'
    actual_result = trackhubs.translator.save_and_update_document(fake_hub_url, data_type='genomics', current_user=user)
    expected_result = {'success': 'The hub is submitted successfully'}
    assert actual_result == expected_result


@pytest.mark.parametrize(
    'hub_url, expected_result',
    [
        ('https://url/to/non/existing/hub.txt', None),
        ('https://url/to/the/hub.txt', {'error': 'The Hub is already submitted, please delete it before resubmitting '
                                                 'it again'}),
    ]
)
@pytest.mark.django_db
def test_save_and_update_document_fail(hub_url, expected_result, create_user_resource, create_hub_resource):
    user, _ = create_user_resource

    actual_result = trackhubs.translator.save_and_update_document(hub_url, data_type='genomics', current_user=user)
    assert actual_result == expected_result
