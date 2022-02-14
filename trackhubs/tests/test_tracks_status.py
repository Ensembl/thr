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
from trackhubs.tracks_status import fix_big_data_url, check_response

# disable logging when running tests
logging.disable(logging.CRITICAL)


@pytest.mark.parametrize(
    'big_data_url, trackdb_url, expected_result',
    [
        ('foo.bb', 'https://random.org/fake/url/trackdb.txt', 'https://random.org/fake/url/foo.bb'),
        ('https://random.org/fake/url/foo.bb', 'https://random.org/fake/url/trackdb.txt', 'https://random.org/fake/url/foo.bb'),
    ]
)
def test_fix_big_data_url(big_data_url, trackdb_url, expected_result):
    actual_result = fix_big_data_url(big_data_url, trackdb_url)
    assert actual_result == expected_result


@pytest.mark.parametrize(
    'big_data_url, expected_result',
    [
        ('http://expdata.cmmt.ubc.ca/JASPAR/downloads/UCSC_tracks/2020/JASPAR2020_hg38.bb', 200),
        ('ftp://ftp.sra.ebi.ac.uk/vol1/ERZ113/ERZ1131357/SRR2922672.cram', "ftp error: error_perm('550 Failed to change directory.')"),
        ('ftp://ftp.sra.ebi.ac.uk/bar.cram', "ftp error: URLError(\"ftp error: error_perm('550 Failed to change directory.')\")"),
        ('http://some.org/random/url/foo.cram', '403: Forbidden'),
    ]
)
def test_check_response(big_data_url, expected_result):
    actual_result = check_response(big_data_url)
    assert actual_result == expected_result
