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
from argparse import RawTextHelpFormatter

from django.core.management.base import BaseCommand
import logging

from trackdbs.update_trackdb import update_all_trackdbs, update_one_trackdb
from trackhubs.tracks_status import fetch_tracks_status
import trackhubs.models
from django.core import management

logger = logging.getLogger(__name__)
# show logs in the console
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Command(BaseCommand):
    help = """
        Update trackdb (bigDataUrl) status both in ES and MySQL
        Also updates 'configuration' and 'data' fields in ES
        This enrich command is used only for data loaded from the old THR's ES
        
        Usage:
            # Update status of trackdb with the ID 10001
            $ python manage.py enrich 10001
            # Update status of all trackdbs
            $ python manage.py enrich all
            # Update status of all trackdbs excluding 
            $ python manage.py enrich all --exclude
        
        Trackdb Examples:
            LNCipedia 3.1: Remote Data Unavailable
            SRP062127: All is Well
    """

    def create_parser(self, *args, **kwargs):
        """
        Insert newline in the help text
        See: https://stackoverflow.com/a/35470682/4488332
        """
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        # This is mandatory argument
        parser.add_argument(
            'trackdbid',
            type=str,
            help="Update trackdb status by providing the <id> or 'all' \nif you want to update all trackdbs status",
        )
        # This is an optional argument
        parser.add_argument(
            '--exclude',
            type=str,
            help="Trackdb ID that will be excluded (e.g Blueprint Hub), works only with 'all'",
        )

    def handle(self, *args, **options):
        # uncomment the line below if you want to rebuild and enrich the index at the same time
        # it's commented because it takes time on k8s and keep causing timeout error
        # management.call_command("search_index", "--rebuild", "-f")
        # Updating process:
        # Get the trackdb ID if provided
        trackdb_id = options['trackdbid'] if options['trackdbid'] is not None else None
        if options['trackdbid'].lower() == 'all':
            # if 'all' check if a trackdb ID is/is not excluded
            excluded_trackdb_id = options['exclude']
            if excluded_trackdb_id is not None and excluded_trackdb_id.isnumeric():
                update_all_trackdbs(excluded_trackdb=excluded_trackdb_id)
                self.stdout.write(self.style.SUCCESS(f"All TrackDB are updated successfully (Except Trackdb with ID: {excluded_trackdb_id})!"))
            else:
                update_all_trackdbs()
                self.stdout.write(self.style.SUCCESS('All TrackDB are updated successfully!'))
        else:
            # Update one specific trackdb
            update_one_trackdb(trackdb_id)
            self.stdout.write(self.style.SUCCESS(f"TrackDB with ID '{trackdb_id}' updated successfully!"))
