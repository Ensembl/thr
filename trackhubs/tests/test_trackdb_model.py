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

import elasticsearch
import pytest

from thr.settings import ELASTICSEARCH_DSL


@pytest.fixture
def es_instance():
    es = elasticsearch.Elasticsearch(
        [ELASTICSEARCH_DSL['default']['hosts']],
        verify_certs=True
    )
    return es


def test_connection(es_instance):
    """
    This function test the connection to the actual Elasticsearch
    """
    # ping() returns whether the cluster is running or not
    assert es_instance.ping()


def test_update_trackdb_document(es_instance, create_trackdb_resource, create_hub_resource):
    """
    Test update_trackdb_document() function
    :param es_instance: Elasticsearch instance created using es_instance fixture
    :param create_trackdb_resource: Fixture that creates the trackdb object
    :param create_hub_resource: Fixture that creates the hub object
    """
    index = 'test_trackhubs'
    doc_type = 'doc'

    trackdb_configuration = {
        "SAMN08391522": {
            "description_url": "ftp://ftp.ensemblgenomes.org/pub/misc_data/Track_Hubs/SRP131250/JGI2.0/SAMN08391522.html",
            "longLabel": "M. brunnea f.sp. Multigermtubi (M.b) treatment ; <a href=\"http://www.ebi.ac.uk/ena/data/view/SAMN08391522\">SAMN08391522</a>",
            "members": {
                "SRR6509755": {
                    "bigDataUrl": "http://ftp.sra.ebi.ac.uk/vol1/ERZ587/ERZ587036/SRR6509755.cram",
                    "parent": "SAMN08391522",
                    "visibility": "pack",
                    "longLabel": "Illumina HiSeq 2000 sequencing; GSM2947191: M. brunnea f.sp. Multigermtubi (M.b) treatment; Populus trichocarpa; RNA-Seq ; <a href=\"http://www.ebi.ac.uk/ena/data/view/SRR6509755\">SRR6509755</a>",
                    "shortLabel": "ENA Run:SRR6509755",
                    "track": "SRR6509755",
                    "type": "cram"
                }
            },
            "shortLabel": "BioSample:SAMN08391522",
            "superTrack": "on show",
            "track": "SAMN08391522",
            "type": "cram"
        },
    }

    expected_trackdb_document = {
        'public': True,
        'source_url': 'http://some.random/url/for/trackDb.txt',
        'data': [
            {
                'id': 'track_obj.fake.id',
                'name': 'track_obj.fake.name'
            }
        ],
        'file_type': {'bam': 1},
        'configuration': trackdb_configuration
    }

    track_status = {
        "last_update": 1562454023,
        "message": "All is Well",
        "tracks": {
            "total": 2,
            "with_data": {
                "total": 1,
                "total_ko": 0
            }
        }
    }

    indexed_trackdb_document = es_instance.index(index=index, doc_type=doc_type, id=1, body=expected_trackdb_document)
    # assert that either the document is created or updated
    assert indexed_trackdb_document['result'] in ('created', 'updated')
    assert create_trackdb_resource.source_url == expected_trackdb_document['source_url']
    assert create_trackdb_resource.public == expected_trackdb_document['public']

    create_trackdb_resource.update_trackdb_document(
        hub=create_hub_resource,
        trackdb_data=expected_trackdb_document['data'],
        trackdb_configuration=expected_trackdb_document['configuration'],
        tracks_status=track_status,
        index=index,
        doc_type=doc_type
    )

    # get the actual trackdb document to compare it with expected data
    actual_trackdb_document = es_instance.get(
        index=index,
        doc_type=doc_type,
        id=create_trackdb_resource.trackdb_id
    )['_source']

    assert actual_trackdb_document['data'] == expected_trackdb_document['data']
    assert actual_trackdb_document['file_type'] == expected_trackdb_document['file_type']
    assert actual_trackdb_document['configuration'] == expected_trackdb_document['configuration']


def test_get_trackdb_file_type_count(create_trackdb_resource, create_track_resource):
    expected_result = {'bam': 1}
    actual_result = create_trackdb_resource.get_trackdb_file_type_count()
    assert actual_result == expected_result


def test_generate_browser_links(create_trackdb_resource):
    expected_result = {
        'ensembl': 'http://grch37.ensembl.org/TrackHub?url=https://url/to/the/hub.txt;species=Homo_sapiens;name=JASPAR%20TFBS;registry=1',
        'vectorbase': 'https://www.vectorbase.org/TrackHub?url=https://url/to/the/hub.txt;species=Homo_sapiens;name=JASPAR%20TFBS;registry=1'
    }
    actual_result = create_trackdb_resource.generate_browser_links()
    assert actual_result == expected_result
