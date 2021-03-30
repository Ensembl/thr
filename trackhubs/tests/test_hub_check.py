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
import pytest

from thr.settings import BASE_DIR
from trackhubs.hub_check import hub_check


@pytest.fixture
def project_dir():
    return BASE_DIR.parent


@pytest.mark.parametrize(
    'test_hub_url, expected_key_in_result',
    [
        ('local:' + str(BASE_DIR.parent) + '/' + 'samples/JASPAR_TFBS/hub.txt', 'success'),
        ('local:' + str(BASE_DIR.parent) + '/' + 'samples/SRP066358/hub.txt', 'warning'),
        ('local:' + str(BASE_DIR.parent) + '/' + 'samples/not/here/hub.txt', 'error'),
    ]
)
def test_hub_check_all_cases(test_hub_url, expected_key_in_result):
    """
    Test hubCheck utility in the three different scenarios
    """
    actual_result = hub_check(test_hub_url)
    assert expected_key_in_result in actual_result
