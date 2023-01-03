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
# import trackhubs
from trackhubs.constants import FILE_TYPES, DATA_TYPES, VISIBILITY
from trackhubs import translator, models


@pytest.mark.django_db
def test_save_datatype_filetype_visibility():
    translator.save_datatype_filetype_visibility(DATA_TYPES, models.DataType)
    translator.save_datatype_filetype_visibility(FILE_TYPES, models.FileType)
    translator.save_datatype_filetype_visibility(VISIBILITY, models.Visibility)

    saved_datatypes_count = models.DataType.objects.all().count()
    saved_filetypes_count = models.FileType.objects.all().count()
    saved_visibilities_count = models.Visibility.objects.all().count()

    assert saved_datatypes_count == len(DATA_TYPES)
    assert saved_filetypes_count == len(FILE_TYPES)
    assert saved_visibilities_count == len(VISIBILITY)


@pytest.mark.django_db
def test_get_datatype_filetype_visibility():
    actual_datatype_obj = models.DataType.objects.create(name='genomics')
    expected_datatype_obj = translator.get_datatype_filetype_visibility('genomics', models.DataType)
    assert actual_datatype_obj == expected_datatype_obj

    actual_filetype_obj = models.FileType.objects.create(name='bam')
    expected_filetype_obj = translator.get_datatype_filetype_visibility('bam', models.FileType)
    assert actual_filetype_obj == expected_filetype_obj

    actual_visibility_obj = models.Visibility.objects.create(name='hide')
    expected_visibility_obj = translator.get_datatype_filetype_visibility('hide', models.Visibility)
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
    assert expected_hub_info['shortLabel'] == create_hub_resource.shortLabel
    assert expected_hub_info['longLabel'] == create_hub_resource.longLabel
    assert expected_hub_info['email'] == create_hub_resource.email
    assert expected_hub_info['descriptionUrl'] == create_hub_resource.description_url
    assert expected_hub_info['url'] == create_hub_resource.url


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
    assert expected_track_info['shortLabel'] == create_track_resource.shortLabel
    assert expected_track_info['longLabel'] == create_track_resource.longLabel
    assert expected_track_info['bigDataUrl'] == create_track_resource.big_data_url


@pytest.mark.parametrize(
    'string_with_spaces, expected_result',
    [
        ('bigBed 6 +', 'bigBed'),  # space
        ('bigBed    6 +', 'bigBed'),  # tab
    ]
)
def test_get_first_word(string_with_spaces, expected_result):
    actual_result = translator.get_first_word(string_with_spaces)
    assert expected_result == actual_result


@pytest.mark.django_db
def test_add_parent_id(create_track_resource, create_child_track_resource):
    parent_name = 'JASPAR2020_TFBS_hg19 off'
    parent_track = translator.add_parent_id(
        parent_name=parent_name,
        current_track=create_child_track_resource
    )
    # assert that the added parent id is actually the parent id
    assert parent_track.track_id == create_child_track_resource.parent_id


@pytest.mark.django_db
def test_get_parents(create_child_track_with_parent_resource):
    parent_track, grandparent_track = translator.get_parents(create_child_track_with_parent_resource)
    assert parent_track.track_id == create_child_track_with_parent_resource.parent_id
    assert grandparent_track is None


@pytest.mark.parametrize(
    'hub_url, expected_result',
    [
        ('https://url/to/the/hub.txt', models.Hub()),
        ('https://url/to/non/existing/hub.txt', None),
    ]
)
@pytest.mark.django_db
def test_is_hub_exists(hub_url, expected_result, create_hub_resource):
    actual_result = translator.is_hub_exists(hub_url)
    assert isinstance(actual_result, type(expected_result))


@pytest.mark.django_db
def test_save_and_update_document_success(project_dir, create_user_resource, create_genome_assembly_dump_resource):
    user, _ = create_user_resource

    # fake_hub_url = 'file:///' + str(project_dir) + '/' + 'samples/JASPAR_TFBS/hub.txt'
    fake_hub_url = 'https://raw.githubusercontent.com/Ensembl/thr/master/samples/JASPAR_TFBS/hub.txt'
    actual_result = translator.save_and_update_document(fake_hub_url, data_type='genomics', current_user=user)
    expected_result = {'success': 'The hub is submitted/updated successfully'}
    assert actual_result == expected_result


@pytest.mark.parametrize(
    'hub_url, expected_error_key_result',
    [
        ('https://url/to/the/hub.txt', 'error'),
    ]
)
@pytest.mark.django_db
def test_save_and_update_document_fail(hub_url, expected_error_key_result, create_user_resource, create_hub_resource):
    user, _ = create_user_resource

    actual_result = translator.save_and_update_document(hub_url, data_type='genomics', current_user=user)
    assert expected_error_key_result in actual_result
