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


def update_all_trackdbs():
    """
    This function will be executed automatically via cron.
    It checks and updates all trackdb (bigDataUrl) status
    both in ES and MySQL
    """
    all_trackdbs = trackhubs.models.Trackdb.objects.all()
    trackdbs_counter = 0
    total_trackdbs = len(all_trackdbs)
    for trackdb in all_trackdbs:
        update_one_trackdb(trackdb.trackdb_id)
        trackdbs_counter += 1
        print(f"{trackdbs_counter}/{total_trackdbs} trackdbs enriched/processed", end='\r')
    print(f"{total_trackdbs} trackdbs enriched")


def update_one_trackdb(trackdb_id):
    """
    Update the status of one specific trackdb and enrich ES docs
    """
    # Get the current trackdb object
    one_trackdb = trackhubs.models.Trackdb.objects.filter(trackdb_id=trackdb_id).first()
    # Get all tracks belonging to the current trackdb object
    all_tracks = trackhubs.models.Track.objects.filter(trackdb_id=trackdb_id)

    if one_trackdb:
        tracks_status = fetch_tracks_status(all_tracks, one_trackdb.source_url)
        # Update the status JSON field in MySQL
        one_trackdb.status = tracks_status
        one_trackdb.save()
        # Update ES document
        one_trackdb.update_trackdb_document(one_trackdb.hub, one_trackdb.data, one_trackdb.configuration, tracks_status)
        logger.info('Status updated successfully: ', tracks_status)

    return one_trackdb
