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

from trackhubs.translator import save_and_update_document
from trackhubs.models import Hub


def boolean_input(question, default=None):
    result = input("%s " % question)
    if not result and default is not None:
        return default
    while len(result) < 1 or result[0].lower() not in 'yn':
        result = input('Please answer yes or no: ')
    return result[0].lower() == "y"


class Command(BaseCommand):
    help = """
        Enrich elasticsearch index based on data stored in MySQL DB, or, 
        if a new hub url is provided, which doesn't exist in the DB
        the user will be asked whether he want to load it or not
    """

    def add_arguments(self, parser):
        parser.add_argument('--huburl', nargs='+', type=str, help='Valid Hub URL')

    def handle(self, *args, **options):
        # this portion is used to enrich/load specific hub(s) by providing the hub url
        # e.g. python manage.py enrich --huburl https://data.broadinstitute.org/compbio1/PhyloCSFtracks/trackHub/hub.txt
        if options['huburl'] is not None:
            for hub_url in options['huburl']:
                # Check if the hub already exist in the db
                # if it's the case update it, if it's not
                # the user is asked whether he want to load the new hub or not
                existing_hub_obj = Hub.objects.filter(url=hub_url).first()
                if existing_hub_obj:
                    try:
                        save_and_update_document(hub_url)
                    except TypeError:
                        raise CommandError("Hub url '{}' is not valid".format(hub_url))
                    except IndexError:
                        raise CommandError(
                            "'{}' is not valid, please make sure that the text file is formatted correctly".format(
                                hub_url))
                    else:
                        self.stdout.write(self.style.SUCCESS("The Hub '{}' is updated successfully".format(hub_url)))
                else:
                    answer = boolean_input("The hub with the url '{}' doesn't exist in the database.\ndo you want to add it and proceed with the enrichment? [y/n]".format(hub_url))
                    if answer:
                        save_and_update_document(hub_url)
                        self.stdout.write(self.style.SUCCESS("The Hub '{}' is loaded successfully".format(hub_url)))
                    else:
                        self.stdout.write(self.style.WARNING("The Hub '{}' is not loaded".format(hub_url)))

        # the command below will enrich all hubs stored in the DB
        # e.g. python manage.py enrich
        else:
            all_hubs = Hub.objects.all()
            for hub in all_hubs:
                save_and_update_document(hub.url)
            self.stdout.write(self.style.SUCCESS('All Hubs are updated successfully'))
