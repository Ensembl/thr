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
import sys
from pathlib import Path

from django.conf import settings


HUBCHECK_PATH = settings.BASE_DIR.parent / "tools" / "hubCheck"
HUBCHECK_DOWNLOAD_URLS = {
    "linux": "http://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64/hubCheck",
    "darwin": "http://hgdownload.soe.ucsc.edu/admin/exe/macOSX.arm64/hubCheck",
}


def _ensure_hubcheck_binary():
    """
    Download hubCheck into the local tools directory if it is not already present.
    """
    hubcheck = Path(HUBCHECK_PATH)
    if hubcheck.exists():
        hubcheck.chmod(0o700)
        return None

    download_url = HUBCHECK_DOWNLOAD_URLS.get(sys.platform)
    if not download_url:
        return {"error": "hubCheck is not available for platform '{}'".format(sys.platform)}

    hubcheck.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(["curl", "-L", "-o", str(hubcheck), download_url], check=True)
        hubcheck.chmod(0o700)
    except (OSError, subprocess.CalledProcessError) as exc:
        return {"error": "Couldn't download hubCheck: {}".format(exc)}

    return None


def hub_check(hub_url):
    """
    Runs the UCSC hubCheck tool on the submitted hub
    :param hub_url: the hub url provided by the submitter
    :returns: the hub information if the submission was successful otherwise it returns an error
    TODO: group 'translator.py', 'hub_check.py', 'constants' and 'parser.py' in 'utils' directory
    """
    download_error = _ensure_hubcheck_binary()
    if download_error:
        return download_error

    print("[INFO] Checking " + hub_url + "...")
    try:
        hub_check_result = subprocess.run(
            [str(HUBCHECK_PATH), "-noTracks", hub_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
    except OSError as exc:
        return {"error": "Couldn't run hubCheck: {}".format(exc)}

    lines = hub_check_result.stdout.splitlines()
    line_0 = lines[0] if lines else ""
    other_lines = lines[1:]

    # hubCheck exits with code 1 even if there are only warnings.
    # Treat warning-only output as a warning response, and any non-warning line
    # after the header as an error.
    warnings = []
    errors = []
    if hub_check_result.returncode:
        for line in other_lines:
            if line.startswith("warning:"):
                warnings.append(line)
            else:
                errors.append(line)

        if errors or not warnings:
            return {
                'error': 'Error in hub {}: {}'.format(hub_url, line_0.strip(':')),
                'details': errors or other_lines or [line_0],
            }

        return {
            'warning': 'Warnings found (they can be ignored)',
            'details': warnings,
        }

    return {
        'success': 'hubCheck done! Nothing to report!'
    }
