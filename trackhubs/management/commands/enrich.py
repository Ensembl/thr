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
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

from trackhubs.translator import save_and_update_document
import trackhubs.models


class Command(BaseCommand):
    help = """
        Enrich elasticsearch index based on data stored in MySQL DB
    """

    def _enrich_docs(self):
        all_trackdbs = trackhubs.models.Trackdb.objects.all()
        for trackdb in all_trackdbs:
            trackdb.update_trackdb_document(trackdb.hub, trackdb.data, trackdb.configuration)

    def handle(self, *args, **options):
        # the command below will enrich all trackdbs stored in the DB
        # e.g. python manage.py enrich
        self._enrich_docs()
        self.stdout.write(self.style.SUCCESS('All documents are updated successfully!'))
