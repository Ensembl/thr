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
import requests
from thr import settings


def hub_check(hub_url):
    """
    Runs the USCS hubCheck API on the submitted hub
    :param hub_url: the hub url provided by the submitter
    :returns: the hub information if the submission was successful otherwise it returns an error
    TODO: group 'translator.py', 'hub_check.py', 'constants' and 'parser.py' in 'utils' directory
    """
    url = settings.HUBCHECK_API_URL
    payload = {"hub_url": hub_url}

    print("[INFO] Checking " + hub_url + "...")
    response = requests.get(url, params=payload)
    if not response.ok:
        print("Couldn't run hubCheck, reason: %s [%d]" % (response.text, response.status_code))
        sys.exit()

    hub_check_result = response.json()
    return hub_check_result
