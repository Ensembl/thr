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
import time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from argparse import RawTextHelpFormatter

User = get_user_model()

def import_users_dump(filepath):
    """
    Parse users data stored in the JSON file and load it in user MySQL table
    :param filepath: path to JSON file
    :returns: an integer representing the number of rows added to the database
    if an error occurred or the file wasn't found it returns None
    """
    try:
        with open(filepath) as f:
            users_info = json.load(f)

        if users_info:
            for user_info in users_info:
                # create the user if he doesn't exist
                user, created = User.objects.get_or_create(
                    username=user_info.get('username'),
                    email=user_info.get('email'),
                    password=user_info.get('password'),
                    first_name=user_info.get('first_name'),
                    last_name=user_info.get('last_name'),
                    continuous_alert=user_info.get('continuous_alert'),
                    affiliation=user_info.get('affiliation'),
                    check_interval='automatic',
                )
                user.is_active = False
                user.is_superuser = False
                user.save()
            return len(users_info)

    except FileNotFoundError:
        print("File {} not found!".format(filepath))

    except Exception as e:
        print(e)

    return None


class Command(BaseCommand):
    help = """
        Dump users from the old MySQL DB to the new one
        it will be used only once
        Usage:
        $ python manage.py import_users
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
        start = time.time()

        json_dump_file = 'samples/users_sample.json'
        users_count = import_users_dump(json_dump_file)

        if users_count is not None:
            end = time.time()
            self.stdout.write(self.style.SUCCESS(
                '[USERS] {} objects imported successfully to MySQL DB (took {} seconds)!'.format(users_count, round(end - start, 2))
            ))
        else:
            self.stdout.write(self.style.ERROR("""
                An unexpected error occurred, please see the exception error above
            """
            ))
