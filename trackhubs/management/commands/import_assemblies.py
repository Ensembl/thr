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
from trackhubs.constants import INSDC_TO_UCSC


def import_ena_dump(filepath):
    """
    Parse genome assembly data stored in the JSON file and load it in genome_assembly_dump MySQL table
    :param filepath: path to JSON file
    :returns: an integer representing the number of rows added to the database
    if an error occurred or the file wasn't found it returns None
    """
    try:
        with open(filepath) as f:
            data_list = json.load(f)

        if data_list:
            # delete everything in genome_assembly_dump table before loading the JSONs
            GenomeAssemblyDump.objects.all().delete()
            print("All rows are deleted! Please wait, the import process will take a while")

            for data in data_list:
                accession_with_version = data.get('accession') + '.' + data.get('version')
                GenomeAssemblyDump.objects.create(
                    accession=data.get('accession'),
                    version=data.get('version'),
                    accession_with_version=accession_with_version,
                    assembly_name=data.get('assembly_name'),
                    assembly_title=data.get('assembly_title'),
                    tax_id=data.get('tax_id'),
                    scientific_name=data.get('scientific_name'),
                    ucsc_synonym=INSDC_TO_UCSC.get(accession_with_version),
                    api_last_updated=data.get('last_updated')
                )
            return len(data_list)

    except FileNotFoundError:
        print("File {} not found! Please run 'python manage.py import_assemblies --fetch ena' first".format(filepath))

    except Exception as e:
        print(e)

    return None


def fetch_assembly(assembly_source, assembly_url):
    """
    Fetch genome assembly data from ENA and/or UCSC using their API
    and dump it into a JSON file, the file(s) will be used by
    import_ena_dump(filepath) and import_ucsc_dump(filepath)
    to import the data to the databases
    :param assembly_source: assembly source (e.g. ENA, UCSC etc)
    :param assembly_url: assembly URL
    :returns: the json response and how long it took in seconds
    """

    try:
        start = time.time()

        response = requests.get(assembly_url, headers={'Accept': 'application/json'})
        with open('assemblies_dump/'+assembly_source.lower()+'_assembly.json', 'w') as outf:
            # pretty print to JSON file
            outf.write(json.dumps(response.json(), indent=4))

        end = time.time()
        elapsed_time = round(end - start, 2)

        return response.json(), elapsed_time

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
            print("[ENA] Fetching assemblies from ENA, it may take few minutes...")
            ena_main_url = 'https://www.ebi.ac.uk/ena/portal/api'
            ena_fields = 'accession,version,assembly_name,assembly_title,tax_id,scientific_name,last_updated'
            ena_url = ena_main_url + '/search?dataPortal=ena&fields=' + ena_fields + '&format=json&limit=0&offset=0&result=assembly'

            json_response, elapsed_time = fetch_assembly(chosen_source, ena_url)
            fetch_objects_count = len(json_response)

            print("[{}] {} Objects are fetched successfully (took {} seconds)"
                  .format(chosen_source.upper(), fetch_objects_count, elapsed_time))

        elif chosen_source == 'ucsc':
            print("[UCSC] Fetching assemblies from UCSC, it may take few seconds...")
            # fetching UCSC isn't necessary since INSDC_TO_UCSC imported from constants does the job
            # but it can be used to check the available genome assemblies provided by UCSC
            # TODO: keep an eye on any new source that offers INSDC TO UCSC mapping or vice versa
            ucsc_url = 'https://api.genome.ucsc.edu/list/ucscGenomes'

            json_response, elapsed_time = fetch_assembly(chosen_source, ucsc_url)
            fetch_objects_count = len(json_response['ucscGenomes'])

            print("[{}] {} Objects are fetched successfully (took {} seconds)"
                  .format(chosen_source.upper(), fetch_objects_count, elapsed_time))

        else:
            # just import ENA assembly dump
            ena_filepath = 'assemblies_dump/ena_assembly.json'

            count = import_ena_dump(ena_filepath)
            if count is not None:
                end = time.time()
                self.stdout.write(self.style.SUCCESS(
                    '[ENA] {} objects imported successfully to MySQL DB (took {} seconds)!'.format(count, round(end - start, 2))
                ))
            else:
                self.stdout.write(self.style.ERROR("""
                    An unexpected error occurred, please see the exception error above
                """
                ))
