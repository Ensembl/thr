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

import logging
import pytest
from trackhubs.parser import parse_file_from_url

# disable logging when running tests
logging.disable(logging.CRITICAL)


def test_fetch_hub_success():
    hub_url = 'https://data.broadinstitute.org/compbio1/PhyloCSFtracks/trackHub/hub.txt'

    expected_hub_info = {
        "hub": "trackHub",
        "shortLabel": "PhyloCSF",
        "longLabel": "Evolutionary protein-coding potential as measured by PhyloCSF",
        "genomesFile": "genomes.txt",
        "email": "iljungr@csail.mit.edu",
        "descriptionUrl": "hub.DOC.html",
        "url": "https://data.broadinstitute.org/compbio1/PhyloCSFtracks/trackHub/hub.txt"
    }
    actual_result = parse_file_from_url(hub_url, is_hub=True)[0]
    assert expected_hub_info == actual_result


@pytest.mark.parametrize(
    'test_url, expected_result',
    [
        ('https://data.broadinstitute.org/compbio1/PhyloCSFtracks/trackHub/hub.ttxt', None),
        ('https://invalide.url/hub.txt', None),
        ('', None),
        (15, None),
        # TODO: Decide whether to return None or empty list when the user provide an unformatted text url
        ('https://www.le.ac.uk/oerresources/bdra/html/resources/example.txt', [])
    ]
)
def test_fetch_hub_fail(test_url, expected_result):
    actual_result = parse_file_from_url(test_url, is_hub=True)
    assert actual_result == expected_result
