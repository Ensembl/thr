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

from argparse import RawTextHelpFormatter
import logging
from django.core.management.base import BaseCommand
from trackdbs.update_trackdb import update_all_trackdbs

logger = logging.getLogger(__name__)
# show logs in the console
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Command(BaseCommand):
    help = """
        Update trackdb (bigDataUrl) status both in ES and MySQL
        This command will be executed periodically via cronjob 
        
        Usage:
            # Update status of all trackdbs
            $ python manage.py update_status
    """

    def create_parser(self, *args, **kwargs):
        """
        Insert newline in the help text
        See: https://stackoverflow.com/a/35470682/4488332
        """
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Updating all trackdbs status...'))
        # update_all_trackdbs is SLOW, TODO: find a way to speed it up
        update_all_trackdbs()
        self.stdout.write(self.style.SUCCESS('All TrackDB status are updated successfully!'))


