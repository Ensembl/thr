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

from elasticsearch import Elasticsearch
from thr.settings import ELASTICSEARCH_DSL


def test_connection():
    es = Elasticsearch(
        [ELASTICSEARCH_DSL['default']['hosts']],
        verify_certs=True
    )
    # ping() returns whether the cluster is running or not
    assert es.ping()


def test_add_document():
    es = Elasticsearch(
        [ELASTICSEARCH_DSL['default']['hosts']],
        verify_certs=True
    )

    index = 'test-index'
    expected_document = {
        'id': 1,
        'assembly': 'GRCh37',
        'created': '1600187202',
        'file_type': 'bam',
    }

    # Delete the index if it already exists
    es.indices.delete(index)

    actual_result = es.index(index=index, doc_type=index, id=1, body=expected_document)['result']
    assert actual_result == 'created'

    es.indices.refresh(index)

    actual_document = es.get(index=index, doc_type=index, id=1)['_source']
    assert actual_document == expected_document
