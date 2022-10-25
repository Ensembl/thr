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

from io import StringIO

import pytest
from django.core.management import call_command
from trackhubs.utils import escape_ansi


@pytest.mark.django_db
def test_enrich_all_success(create_trackdb_resource):
    out = StringIO()
    call_command('enrich', 'all', stdout=out)
    assert 'All TrackDB are updated successfully!\n' == escape_ansi(out.getvalue())


@pytest.mark.django_db
def test_enrich_one_success(create_trackdb_resource):
    out = StringIO()
    call_command('enrich', '1', stdout=out)
    assert "TrackDB with ID '1' updated successfully!\n" == escape_ansi(out.getvalue())


@pytest.mark.django_db
def test_enrich_one_fail():
    out = StringIO()
    call_command('enrich', '1', stdout=out)
    assert "No TrackDB with ID '1'!\n" == escape_ansi(out.getvalue())
