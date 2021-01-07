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

import json
import requests
import time

from django.core.management.base import BaseCommand
from argparse import RawTextHelpFormatter
from trackhubs.models import GenomeAssemblyDump


def import_ena_dump(filepath):
    try:
        with open(filepath) as f:
            data_list = json.load(f)

        if data_list:
            # delete everything in genome_assembly_dump table before loading the JSONs
            GenomeAssemblyDump.objects.all().delete()
            print("All rows are deleted!")

            for data in data_list:
                GenomeAssemblyDump.objects.create(
                    accession=data.get('accession'),  # data.get('accession') + '.' + accession=data.get('version') ?
                    version=data.get('version'),
                    assembly_name=data.get('assembly_name'),
                    assembly_title=data.get('assembly_title'),
                    tax_id=data.get('tax_id'),
                    scientific_name=data.get('scientific_name'),
                    api_last_updated=data.get('last_updated')
                )
            return len(data_list)

    except FileNotFoundError:
        print("File not found! PLease run 'python manage.py import_assemblies --fetch ena' first")

    except Exception as e:
        print(e)

    return None


def fetch_ena_assembly():
    main_url = 'https://www.ebi.ac.uk/ena/portal/api'
    fields = 'accession,version,assembly_name,assembly_title,tax_id,scientific_name,last_updated'

    url = main_url + '/search?dataPortal=ena&fields=' + fields + '&format=json&limit=5&offset=0&result=assembly'
    headers = {'Accept': 'application/json'}

    try:
        print("[ENA] Fetching assemblies from ENA, it may take few minutes...")
        start = time.time()
        response = requests.get(url, headers=headers)

        with open('assemblies_dump/ena_assembly.json', 'wb') as outf:
            outf.write(response.content)

        end = time.time()
        fetch_elapsed_time = round(end - start, 2)
        fetch_objects_count = len(response.json())
        print("[ENA] {} Objects are fetched successfully (took {} seconds)"
              .format(fetch_objects_count, fetch_elapsed_time))

    except Exception as e:
        print(e)


class Command(BaseCommand):
    help = """
        Dump assemblies mapping from external APIs of different sources (ENA, ENSEMBL and UCSC)
        and/or import JSONs to MySQL table 'genome_assembly_dump' which will be used to populate
        assembly an species table with th appropriate information when the user submit a hub.
        Usage:
        # import genome assemblies from all JSONs files without fetching data from external API(s)
        $ python manage.py import_assemblies
        # fetch assemblies info from <source> and import all JSONs files to genome_assembly_dump table
        # <source> can be 'ena', 'ensembl' or 'ucsc' (without quotes)
        $ python manage.py import_assemblies --fetch <source>
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
        # This is an optional argument
        parser.add_argument(
            '--fetch',
            type=str,
            help="fetch assemblies info from <source>, <source> can be 'ena', 'ensembl' or 'ucsc' (without quotes)",
        )

    def handle(self, *args, **options):
        start = time.time()
        chosen_source = options['fetch'].lower() if options['fetch'] is not None else None

        if chosen_source == 'ena':
            print("options['fetch']  --> {}".format(options['fetch']))
            fetch_ena_assembly()

        ena_filepath = 'assemblies_dump/ena_assembly.json'

        count = import_ena_dump(ena_filepath)
        if count is not None:
            end = time.time()
            self.stdout.write(self.style.SUCCESS(
                '[ENA] {} objects imported successfully to MySQL DB (took {} seconds)!'.format(count, round(end - start, 2))
            ))
        else:
            self.stdout.write(self.style.ERROR("""
                An unexpected error occurred, please see the exception error above,
            """
            ))
