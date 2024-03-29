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
from trackhubs.parser import parse_file_from_url

# disable logging when running tests
logging.disable(logging.CRITICAL)


def test_parse_hub_success(project_dir):
    # fake_hub_url = 'file:///' + str(project_dir) + '/' + 'samples/JASPAR_TFBS/hub.txt'
    fake_hub_url = 'https://raw.githubusercontent.com/Ensembl/thr/master/samples/JASPAR_TFBS/hub.txt'

    expected_hub_info = {
        'hub': 'JASPAR_TFBS',
        'shortLabel': 'JASPAR TFBS',
        'longLabel': 'TFBS predictions for profiles in the JASPAR CORE collections',
        'genomesFile': 'genomes.txt',
        'email': 'wyeth@cmmt.ubc.ca',
        'descriptionUrl': 'http://jaspar.genereg.net/genome-tracks/',
        'url': fake_hub_url
    }
    actual_result = parse_file_from_url(fake_hub_url)[0]
    assert expected_hub_info == actual_result


def test_parse_genomes_success(project_dir):
    # fake_genomes_url = 'file:///' + str(project_dir) + '/' + 'samples/JASPAR_TFBS/genomes.txt'
    fake_genomes_url = 'https://raw.githubusercontent.com/Ensembl/thr/master/samples/JASPAR_TFBS/genomes.txt'

    expected_genomes_info = [
        {
            'genome': 'hg19',
            'trackDb': 'hg19/trackDb.txt',
            'url': fake_genomes_url
        },
        {
            'genome': 'hg38',
            'trackDb': 'hg38/trackDb.txt',
            'url': fake_genomes_url
        }
    ]
    actual_result = parse_file_from_url(fake_genomes_url)
    assert expected_genomes_info == actual_result


def test_parse_trackdbs_success(project_dir):
    # fake_trackdbs_url = 'file:///' + str(project_dir) + '/' + 'samples/JASPAR_TFBS/hg19/trackDb.txt'
    fake_trackdbs_url = 'https://raw.githubusercontent.com/Ensembl/thr/master/samples/JASPAR_TFBS/hg19/trackDb.txt'

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
            'url': fake_trackdbs_url
        }
    ]
    actual_result = parse_file_from_url(fake_trackdbs_url)
    assert expected_trackdbs_info == actual_result


@pytest.mark.parametrize(
    'test_url, expected_result',
    [
        ('https://data.broadinstitute.org/compbio1/PhyloCSFtracks/trackHub/hub.ttxt', None),
        ('https://invalide.url/hub.txt', None),
        ('', None),
        (15, None)
    ]
)
def test_parse_url_fail(test_url, expected_result):
    actual_result = parse_file_from_url(test_url)
    assert actual_result == expected_result
