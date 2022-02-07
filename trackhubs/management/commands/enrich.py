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
import sys

from django.core.management.base import BaseCommand
import logging
from trackhubs.tracks_status import fetch_tracks_status
import trackhubs.models
from django.core import management

logger = logging.getLogger(__name__)
# show logs in the console
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Command(BaseCommand):
    help = """
        Enrich elasticsearch index based on data stored in MySQL DB
    """

    def _enrich_docs(self):
        all_trackdbs = trackhubs.models.Trackdb.objects.all()
        not_enriched_hubs_ids = []
        trackdbs_counter = 0
        total_trackdbs = len(all_trackdbs)
        for trackdb in all_trackdbs:
            tracks_status = fetch_tracks_status(trackdb.__dict__, trackdb.source_url)
            # this try except is to handle the error
            # UnicodeDecodeError: 'utf-8' codec can't decode byte 0x92 in position 199: invalid start byte
            # e.g. hub "VBRNAseq_group_1464"
            try:
                hub = trackhubs.models.Hub.objects.get(hub_id=trackdb.hub_id)
                trackdb.update_trackdb_document(hub, trackdb.data, trackdb.configuration, tracks_status)
            # we ignore them for now, TODO: investigate/solve this later
            # more details here: https://www.ebi.ac.uk/seqdb/confluence/x/3ympCQ
            # UPDATE: This issue may never appear again if the cause was me manually changing the DB CHARSET
            except UnicodeDecodeError as unicode_err:
                not_enriched_hubs_ids.append(trackdb.hub_id)
                logger.debug("Hub id {} couldn't be enriched, reason: {}".format(trackdb.hub_id, unicode_err))

            trackdbs_counter += 1
            print('{}/{} trackdbs enriched/processed'.format(trackdbs_counter, total_trackdbs), end='\r')

        logger.debug("Not Enriched Hubs IDs: ", not_enriched_hubs_ids)
        not_enriched_hubs_len = len(list(set(not_enriched_hubs_ids)))
        print("{} hubs enriched".format(total_trackdbs - not_enriched_hubs_len))
        print("{} hubs couldn't be enriched".format(not_enriched_hubs_len))

    def handle(self, *args, **options):
        # uncomment the line below if you want to rebuild and enrich the index at the same time
        # it's commented because it takes time on k8s and keep causing timeout error
        # management.call_command("search_index", "--rebuild", "-f")
        # the command below will enrich all trackdbs stored in the DB
        # e.g. python manage.py enrich
        self._enrich_docs()
        self.stdout.write(self.style.SUCCESS('All documents are updated successfully!'))
