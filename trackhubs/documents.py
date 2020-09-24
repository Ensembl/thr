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

from django_elasticsearch_dsl import Document, ObjectField, fields
from django_elasticsearch_dsl.registries import registry

from .models import Trackdb


@registry.register_document
class TrackdbDocument(Document):

    # set hub fields we want to use
    hub = ObjectField(properties={
        'name': fields.StringField(),
        'longLabel': fields.StringField(),
        'shortLabel': fields.StringField(),
        'url': fields.StringField(),
        'assembly': fields.IntegerField(),
        'browser_links': fields.ObjectField(),
        'empty_object': fields.ObjectField()
    })

    def prepare_hub(self, instance):
        results = instance.hub
        return {
            'name': results['name'],
            'longLabel': results['longLabel'],
            'shortLabel': results['shortLabel'],
            'url': results['url'],
            'assembly': results['assembly'],
            'browser_links': results['browser_links'],
            'empty_object': results['empty_object']
        }

    class Index:
        name = 'trackhubs'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Trackdb

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'id',
            'public',
            'type',
            # 'hub',
            'description',
            'version',
            # 'source',
            # 'species',
            # 'assembly',
            # 'data',
            # 'assembly',
            # 'data',
            # 'configuration',
        ]


def_hub = {
    'longLabel': 'TFBS predictions for all profiles in the JASPAR CORE vertebrates collection (2018)',
    'shortLabel': '',
    'name': 'JASPAR_2018_TFBS',
    'assembly': 0,
    'url': '',
    'empty_object': {},
    'browser_links': {
        'ensembl': 'http://grch37.ensembl.org/TrackHub?url=http://expdata.cmmt.ubc.ca/JASPAR/UCSC_tracks/hub.txt;species=Homo_sapiens;name=JASPAR_2018_TFBS;registry=1',
        'biodalliance': '/biodalliance/view?assembly=hg19&name=JASPAR 2018 TFBS&url=http://expdata.cmmt.ubc.ca/JASPAR/UCSC_tracks/hub.txt',
        'ucsc': 'http://genome.ucsc.edu/cgi-bin/hgHubConnect?db=hg19&hubUrl=http://expdata.cmmt.ubc.ca/JASPAR/UCSC_tracks/hub.txt&hgHub_do_redirect=on&hgHubConnect.remakeTrackHub=on'
    }
}

"""
trackdb = Trackdb(
    id=1,
    public=True,
    type='genomics',
    hub=def_hub,
)
trackdb.save()
"""