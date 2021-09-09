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
import trackhubs
from trackhubs.tracks_status import fetch_tracks_status

logger = logging.getLogger(__name__)


def update_trackdb_status():
    """
    This function will be executed automatically via cron.
    It checks and updates all trackdb (bigDataUrl) status
    both in ES and MySQL
    """
    all_trackdbs = trackhubs.models.Trackdb.objects.all()
    for trackdb in all_trackdbs:
        tracks_status = fetch_tracks_status(trackdb.__dict__, trackdb.source_url)
        # update the status JSON field in MySQL
        # apparently, updating MySQL magically update ES too!
        trackdb.status = tracks_status
        trackdb.save()

        logger.info('Status updated successfully: ', tracks_status)
