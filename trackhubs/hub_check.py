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

import subprocess
from pathlib import Path
from sys import platform


def hub_check(hub_url):
    """
    Runs the USCS hubCheck tool on the submitted hub
    :param hub_url: the hub url provided by the submitter
    :returns: the hub information if the submission was successful otherwise it returns an error
    TODO: group 'translator.py', 'hub_check.py', 'constants' and 'parser.py' in 'utils' directory
    """
    # replacing 'file:///' by 'local:' to avoid 'Unrecognized protocol file in udcProtNew' error
    hub_url = hub_url.replace('file:///', 'local:')
    # Download hubCheck if it doesn't exist in 'tools' directory (in the project root dir) and make it executable
    hubcheck = Path("tools/hubCheck")
    if not Path(hubcheck).exists():
        # consider the OS used and download the appropriate one accordingly
        if platform == "linux":
            subprocess.run(
                ["curl", "-o", "tools/hubCheck", "http://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64/hubCheck"]
            )
        elif platform == "darwin":
            subprocess.run(
                ["curl", "-o", "tools/hubCheck", "http://hgdownload.soe.ucsc.edu/admin/exe/macOSX.x86_64/hubCheck"]
            )

        hubcheck.chmod(0o700)

    print("[INFO] Checking " + hub_url + "...")
    hub_check_result = subprocess.run(
        ["tools/hubCheck", "-noTracks", hub_url],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    print(hub_check_result)

    # hubCheck exits with code 1 even if there are only warnings
    # to fix that, we ignore warning except if an error occurs.
    error = False
    warnings = False
    if hub_check_result.returncode:
        line_0 = hub_check_result.stdout.splitlines()[0]
        other_lines = hub_check_result.stdout.splitlines()[1:]
        for line in other_lines:  # we skip the first line
            if not line.startswith("warning:"):
                error = True
            else:
                warnings = True

    if warnings:
        return {
            'warning': 'Warnings found (they can be ignored)',
            'details': list(war for war in other_lines)
        }

    if error:
        return {
            'error': 'Error in hub {}: {}'.format(hub_url, line_0.strip(':')),
            'details': list(err for err in other_lines)
        }

    return {
        'success': 'hubCheck done! Nothing to report!'
    }
