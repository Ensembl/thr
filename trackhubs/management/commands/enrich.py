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

from django.core.management.base import BaseCommand, CommandError
from elasticsearch_dsl import connections

from trackhubs.parser import update_trackdb_index, parse_file, BDIR, save_file_type


class Command(BaseCommand):
    help = 'Update elasticsearch index.'

    def _update(self):

        cf = {
            'doc': {
                'empty_object': {},
                'browser_links': {
                    'ensembl': 'http://grch37.ensembl.org/TrackHub?url=http://expdata.cmmt.ubc.ca/JASPAR/UCSC_tracks/hub.txt;species=Homo_sapiens;name=JASPAR_2018_TFBS;registry=1',
                    'biodalliance': '/biodalliance/view?assembly=hg19&name=JASPAR 2018 TFBS&url=http://expdata.cmmt.ubc.ca/JASPAR/UCSC_tracks/hub.txt',
                    'ucsc': 'http://genome.ucsc.edu/cgi-bin/hgHubConnect?db=hg19&hubUrl=http://expdata.cmmt.ubc.ca/JASPAR/UCSC_tracks/hub.txt&hgHub_do_redirect=on&hgHubConnect.remakeTrackHub=on'
                }
            }
        }

        es = connections.Elasticsearch()
        es.update(
            index='trackhubs',
            doc_type='doc',
            id=1,
            refresh=True,
            # body={'doc': {
            #     'file_type': {
            #         file_type.name: -1
            #     }
            # }
            # }
            body={'doc': cf}
        )

    def handle(self, *args, **options):
        # Consider when the index doesn't exist
        # self._update()
        self.stdout.write(self.style.SUCCESS('Successfully updated the index'))

