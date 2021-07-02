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
import time
import urllib.request
import urllib.response
import urllib.error
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


def fix_big_data_url(big_data_url, trackdb_url):
    """
    Add URL to file name in case it's not complete (django URLValidator is used here)
    https://docs.djangoproject.com/en/3.1/ref/validators/#urlvalidator
    e.g 'lncipedia_5_2_hg38.bb'
    becomes 'https://lncipedia.org/trackhub/hg38/lncipedia_5_2_hg38.bb'
    :param big_data_url: the bigDataUrl it can be the full URL or the relative path to file
    :param trackdb_url: the trackdb base url that will be used to extract the base url
    which will be added to the relative path
    :returns: the full url
    TODO: rename it to 'relative2absolute_url' and move it to 'utlis.py' file
    """
    trackdb_base_url = trackdb_url[:trackdb_url.rfind('/')]
    validate = URLValidator()
    try:
        validate(big_data_url)
        return big_data_url

    except ValidationError as e:
        return trackdb_base_url + '/' + big_data_url


def check_response(url):
    """
    Check the response
    :param url: the full big_data_url URL
    :returns: 200/None (HTTP/FTP) if everything went well else it returns
    string containing the error code and message
    NOTE:
    check_url makes sure that the URL is 'valid' (it starts with http, ftp ...)
    check_response makes sure that the file exists
    """
    try:
        r = urllib.request.urlopen(url)
        return r.getcode()
    except urllib.error.HTTPError as e:
        # Return code error (e.g. 404, 501, ...)
        logger.error('HTTPError: {}'.format(e.code))
        return "{}: {}".format(e.code, e.reason)
    except urllib.error.URLError as e:
        # Not an HTTP-specific error (e.g. connection refused, FTP errors)
        logger.error('URLError: {}'.format(e.reason))
        return "{}".format(e.reason)


def fetch_tracks_status(trackdb_dict, trackdb_url):
    """
    Create the tracks status dictionary
    :param trackdb_dict: the trackdb dictionary containing all tracks
    :param trackdb_url: the trackdb url (e.g http://lncipedia.org/trackhub/hg38/trackDb.txt),
    it's used by fix_big_data_url() function
    :returns: status dictionary
    """
    total_tracks_with_data = 0
    total_tracks_with_data_ko = 0
    broken_tracks_info = {}

    for track in trackdb_dict:
        if 'bigDataUrl' in track:
            total_tracks_with_data += 1
            # get the full url for the bigDataUrl
            big_data_full_url = fix_big_data_url(track['bigDataUrl'], trackdb_url)
            # make sure it's working
            big_data_exists = check_response(big_data_full_url)
            logger.error("Response of {}: {} ".format(big_data_full_url, big_data_exists))
            # if it's not the case
            if big_data_exists != 200 and big_data_exists is not None:
                total_tracks_with_data_ko += 1
                # fill broken tracks info with the required data
                broken_tracks_info[track['track']] = [big_data_full_url, big_data_exists]

    tracks_status_dict = {
        'last_update': int(time.time()),
        'tracks': {
            'total': len(trackdb_dict),
            'with_data': {
                'total': total_tracks_with_data,
                'total_ko': total_tracks_with_data_ko
            }
        }
    }

    if total_tracks_with_data_ko > 0:
        tracks_status_dict['message'] = 'Remote Data Unavailable'
        # add ko_info to status
        tracks_status_dict['tracks']['with_data']['ko'] = broken_tracks_info
    elif total_tracks_with_data_ko == 0:
        tracks_status_dict['message'] = 'All is Well'
    else:
        tracks_status_dict['message'] = 'Unchecked'

    logger.info("tracks_status_dict: {} ".format(tracks_status_dict))

    return tracks_status_dict
