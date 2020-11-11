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

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import MetaField

from .models import Trackdb


@registry.register_document
class TrackdbDocument(Document):

    hub = fields.ObjectField(properties={
        'name': fields.StringField(),
        'short_label': fields.StringField(),
        'long_label': fields.StringField(),
        'url': fields.StringField(),
        'description_url': fields.StringField(),
        'email': fields.StringField(),
        # 'species': fields.IntegerField(),
        # 'data_type': fields.IntegerField(),
    })

    assembly = fields.ObjectField(properties={
        'accession': fields.StringField(),
    })

    configuration = fields.ObjectField()

    # Meta is used to set dynamic mapping to false to avoid mapping explosion
    # https://www.elastic.co/guide/en/elasticsearch/reference/6.3/mapping.html#mapping-limit-settings
    class Meta:
        all = MetaField(enabled=False)
        dynamic = MetaField('false')

    class Index:
        name = 'trackhubs'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Trackdb

        # The fields of the model we want to be indexed in Elasticsearch
        fields = [
            'public',
            'description',
            'version',
            'created',
            'updated',
            'status_message',
            'status_last_update',
            # 'status',
            'source_url',
            'source_checksum',
        ]
