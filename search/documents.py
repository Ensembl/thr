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

from django.conf import settings
from django_elasticsearch_dsl import Document, Index, fields
from elasticsearch_dsl import analyzer, MetaField

from trackhubs.models import Trackdb


# Name of the Elasticsearch index
INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])

# See Elasticsearch Indices API reference for available settings
INDEX.settings(
    number_of_shards=1,
    number_of_replicas=1
)

html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)


@INDEX.doc_type
class TrackdbDocument(Document):
    """
    Trackdb Elasticsearch document.
    INFO: The TrackdbDocument controls what will be indexed in ES
    the search.api.serializers controls what will be shown after triggering a search query
    """

    type = fields.TextField(
        attr='data_type_indexing',
        analyzer=html_strip,
        fields={
            'raw': fields.KeywordField(),
        }
    )
    
    hub = fields.ObjectField(properties={
        'name': fields.TextField(
            analyzer=html_strip,
            fields={
                'raw': fields.KeywordField(),
            }
        ),
        'short_label': fields.TextField(
            analyzer=html_strip,
            fields={
                'raw': fields.KeywordField(),
            }
        ),
        'long_label': fields.TextField(
            analyzer=html_strip,
            fields={
                'raw': fields.KeywordField(),
            }
        ),
        'url': fields.TextField(
            analyzer=html_strip,
            fields={
                'raw': fields.KeywordField(),
            }
        ),
        'description_url': fields.TextField(
            analyzer=html_strip,
            fields={
                'raw': fields.KeywordField(),
            }
        ),
        'email': fields.TextField(
            analyzer=html_strip,
            fields={
                'raw': fields.KeywordField(),
            }
        ),
    })

    assembly = fields.ObjectField(
        attr='assembly_indexing',
        properties={
            'accession': fields.TextField(
                analyzer=html_strip,
                fields={
                    'raw': fields.KeywordField(),
                }
            ),
            'name': fields.TextField(
                analyzer=html_strip,
                fields={
                    'raw': fields.KeywordField(),
                }
            ),
            'long_name': fields.TextField(
                analyzer=html_strip,
                fields={
                    'raw': fields.KeywordField(),
                }
            ),
            'ucsc_synonym': fields.TextField(
                analyzer=html_strip,
                fields={
                    'raw': fields.KeywordField(),
                }
            ),
    })

    species = fields.ObjectField(
        attr='species_indexing',
        properties={
            'taxon_id': fields.IntegerField(),
            'scientific_name': fields.TextField(
                analyzer=html_strip,
                fields={
                    'raw': fields.KeywordField(),
                }
            ),
            'common_name': fields.TextField(
                analyzer=html_strip,
                fields={
                    'raw': fields.KeywordField(),
                }
            ),
    })

    status = fields.ObjectField()
    configuration = fields.ObjectField()
    data = fields.NestedField()

    class Django:
        """Inner nested class Django."""

        model = Trackdb  # The model associate with this Document

        # The fields of the model we want to be indexed in Elasticsearch
        fields = [
            'trackdb_id',
            'public',
            'description',
            'version',
            'created',
            'updated',
        ]

    # Meta is used to set dynamic mapping to false to avoid mapping explosion
    # https://www.elastic.co/guide/en/elasticsearch/reference/6.3/mapping.html#mapping-limit-settings
    class Meta:
        model = Trackdb
        dynamic = MetaField('false')
