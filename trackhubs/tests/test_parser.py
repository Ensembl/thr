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

import logging
import pytest
from rest_framework.authtoken.models import Token

import trackhubs
from trackhubs.constants import DATA_TYPES, VISIBILITY, FILE_TYPES
from trackhubs.parser import parse_file_from_url, get_datatype_filetype_visibility, save_constant_data, save_hub

# disable logging when running tests
logging.disable(logging.CRITICAL)


@pytest.fixture()
def create_user_resource(django_user_model):
    """
    Create a temporary user and return the token
    """
    user = django_user_model.objects.create_user(username='test_user', password='test-password')
    token, _ = Token.objects.get_or_create(user=user)
    return token


@pytest.fixture()
def create_hub_resource(api_client, create_user_resource):
    """
    This fixture is used to create a temporary trackhub using POST API
    The created trackhub will be used to test GET API
    """
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + create_user_resource.key)
    submitted_hub = {
        "url": "https://raw.githubusercontent.com/Ensembl/thr/feat/add_elasticsearch/samples/JASPAR_TFBS/hub.txt"
    }
    response = api_client.post('/api/trackhub/', submitted_hub, format='json')
    return response


def test_parse_hub_success():
    hub_url = 'https://raw.githubusercontent.com/Ensembl/thr/feat/add_elasticsearch/samples/JASPAR_TFBS/hub.txt'

    expected_hub_info = {
        'hub': 'JASPAR_TFBS',
        'shortLabel': 'JASPAR TFBS',
        'longLabel': 'TFBS predictions for profiles in the JASPAR CORE collections',
        'genomesFile': 'genomes.txt',
        'email': 'wyeth@cmmt.ubc.ca',
        'descriptionUrl': 'http://jaspar.genereg.net/genome-tracks/',
        'url': hub_url
    }
    actual_result = parse_file_from_url(hub_url, is_hub=True)[0]
    assert expected_hub_info == actual_result


def test_parse_genomes_success():
    genomes_url = 'https://raw.githubusercontent.com/Ensembl/thr/feat/add_elasticsearch/samples/JASPAR_TFBS/genomes.txt'

    expected_genomes_info = [
        {
            'genome': 'hg19',
            'trackDb': 'hg19/trackDb.txt',
            'url': genomes_url
        },
        {
            'genome': 'hg38',
            'trackDb': 'hg38/trackDb.txt',
            'url': genomes_url
        }
    ]
    actual_result = parse_file_from_url(genomes_url, is_genome=True)
    assert expected_genomes_info == actual_result


def test_parse_trackdbs_success():
    trackdbs_url = 'https://raw.githubusercontent.com/Ensembl/thr/feat/add_elasticsearch/samples/JASPAR_TFBS/hg19/trackDb.txt'

    expected_trackdbs_info = [
        {
            'track': 'JASPAR2020_TFBS_hg19',
            'shortLabel': 'JASPAR2020 TFBS hg19',
            'longLabel': 'TFBS predictions for all profiles in the JASPAR CORE vertebrates collection (2020)',
            'html': 'http://expdata.cmmt.ubc.ca/JASPAR/UCSC_tracks/JASPAR2020_TFBS_help.html',
            'type': 'bigBed 6 +',
            'maxItems': '100000',
            'labelFields': 'name',
            'defaultLabelFields': 'name',
            'searchIndex': 'name',
            'visibility': 'pack',
            'spectrum': 'on',
            'scoreFilter': '400',
            'scoreFilterRange': '0:1000',
            'bigDataUrl': 'http://expdata.cmmt.ubc.ca/JASPAR/downloads/UCSC_tracks/2020/JASPAR2020_hg19.bb',
            'nameFilterText': '*',
            'url': trackdbs_url
        }
    ]
    actual_result = parse_file_from_url(trackdbs_url, is_trackdb=True)
    assert expected_trackdbs_info == actual_result


@pytest.mark.parametrize(
    'test_url, expected_result',
    [
        ('https://data.broadinstitute.org/compbio1/PhyloCSFtracks/trackHub/hub.ttxt', None),
        ('https://invalide.url/hub.txt', None),
        ('', None),
        (15, None),
        ('https://www.le.ac.uk/oerresources/bdra/html/resources/example.txt', [])
    ]
)
def test_parse_url_fail(test_url, expected_result):
    actual_result = parse_file_from_url(test_url, is_hub=True)
    assert actual_result == expected_result


@pytest.mark.django_db
def test_get_datatype_filetype_visibility():
    actual_visibility_obj = trackhubs.models.Visibility.objects.create(name='genomics')
    actual_visibility_obj.save()
    expected_visibility_obj = get_datatype_filetype_visibility('genomics', trackhubs.models.Visibility)
    assert actual_visibility_obj == expected_visibility_obj


@pytest.mark.django_db
def test_save_constant_data():
    save_constant_data(DATA_TYPES, trackhubs.models.DataType)
    save_constant_data(FILE_TYPES, trackhubs.models.FileType)
    save_constant_data(VISIBILITY, trackhubs.models.Visibility)

    saved_datatypes_count = trackhubs.models.DataType.objects.all().count()
    saved_filetypes_count = trackhubs.models.FileType.objects.all().count()
    saved_visibilities_count = trackhubs.models.Visibility.objects.all().count()

    assert saved_datatypes_count == len(DATA_TYPES)
    assert saved_filetypes_count == len(FILE_TYPES)
    assert saved_visibilities_count == len(VISIBILITY)


@pytest.mark.django_db
def test_save_hub(django_user_model):

    hub_info = {
        'hub': 'JASPAR_TFBS',
        'shortLabel': 'JASPAR TFBS',
        'longLabel': 'TFBS predictions for profiles in the JASPAR CORE collections',
        'genomesFile': 'genomes.txt',
        'email': 'wyeth@cmmt.ubc.ca',
        'descriptionUrl': 'http://jaspar.genereg.net/genome-tracks/',
        'url': 'https://raw.githubusercontent.com/Ensembl/thr/feat/add_elasticsearch/samples/JASPAR_TFBS/hub.txt'
    }

    genomic_datatype_obj = trackhubs.models.DataType(name='genomics')
    genomic_datatype_obj.save()
    expected_datatype = genomic_datatype_obj.name

    # TODO: This species part will be changed when we have a proper species retrieval function
    species_obj = trackhubs.models.Species(taxon_id=9606, scientific_name='Homo sapiens')
    species_obj.save()

    user = django_user_model.objects.create_user(username='temp_user', password='foo_pass')
    actual_hub_obj = save_hub(hub_dict=hub_info, data_type='genomics', current_user=user)

    assert hub_info['hub'] == actual_hub_obj.name
    assert hub_info['shortLabel'] == actual_hub_obj.short_label
    assert hub_info['longLabel'] == actual_hub_obj.long_label
    assert hub_info['email'] == actual_hub_obj.email
    assert hub_info['descriptionUrl'] == actual_hub_obj.description_url
    assert hub_info['url'] == actual_hub_obj.url
    assert expected_datatype == actual_hub_obj.data_type.name

