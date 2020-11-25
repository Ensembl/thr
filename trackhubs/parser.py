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
import urllib.request

logger = logging.getLogger(__name__)


def parse_file_from_url(url, is_hub=False, is_genome=False, is_trackdb=False):
    """
    Parse the hub.txt, genomes.txt and trackdb.txt files from given hub url
    :param url: hub,genomes or trackdb url
    :param is_hub: is set to true if we are parsing a hub
    :param is_genome: is set to true if we are parsing genomes
    :param is_trackdb: is set to true if we are parsing trackdb
    :returns: an array of dictionaries, each dictionary contains one object
    either hub, genome or track
    hub_url examples:
    http://ftp.ebi.ac.uk/pub/databases/ensembl/encode/integration_data_jan2011/hub.txt
    https://data.broadinstitute.org/compbio1/PhyloCSFtracks/trackHub/hub.txt
    ftp://ftp.vectorbase.org/public_data/rnaseq_alignments/hubs/aedes_aegypti/VBRNAseq_group_SRP039093/hub.txt
    http://urgi.versailles.inra.fr/repetdb/repetdb_trackhubs/repetdb_Melampsora_larici-populina_98AG31_v1.0/hub.txt
    """
    logger.info("Parsing '{}'".format(url))
    # dict_info is where key/value of each element (it can be hub, genome or track) is stored
    # e.g. dict_info = {'track': 'JASPAR2020_TFBS_hg19', 'type': 'bigBed 6 +'}
    dict_info = {}
    dict_info_list = []
    try:
        for line in urllib.request.urlopen(url):
            line = line.decode("utf-8").strip()
            # new line marks a new genome/track/supertrack etc
            # in this case we check if dict_info is not empty
            # then we append it to dict_info_list and empty the
            # dictionary fot the next element otherwise (if there is no new line)
            # we read the next line and we repeat the process
            if line in ['\n', '\r\n', '']:
                # check if the dictionary contains either 'hub',
                # 'track', 'genome' before appending it to the list
                # this prevent the submitter from uploading random text file
                is_any = any(i in list(dict_info.keys()) for i in ('hub', 'track', 'genome'))
                if len(dict_info) > 0 and is_any:
                    dict_info.update({'url': url})
                    dict_info_list.append(dict_info)
                    dict_info = {}
                continue

            # there are tracks with hashtag symbol! => ignore them!
            # e.g http://ftp.ebi.ac.uk/pub/databases/ensembl/encode/integration_data_jan2011/hg19/trackDb.txt
            if line.startswith('#'):
                continue

            split_line = line.rstrip('\n').split(' ', 1)
            key = split_line[0].strip()
            dict_info[key] = split_line[1]

        # This part is ugly, but it's the only way I found to make sure the last
        # element is added to the returned dict_info_list (in case there is no new line
        # at the end of the parsed file)
        # TODO: find a better way to detect the EOF
        if (is_hub and 'hub' in dict_info and not any(d.get('hub') == dict_info.get('hub') for d in dict_info_list)) or \
                (is_genome and 'genome' in dict_info and not any(d.get('genome') == dict_info.get('genome') for d in dict_info_list)) or \
                (is_trackdb and 'track' in dict_info and not any(d.get('track') == dict_info.get('track') for d in dict_info_list)):
            dict_info.update({'url': url})
            dict_info_list.append(dict_info)

    except (IOError, urllib.error.HTTPError, urllib.error.URLError, ValueError, AttributeError, TypeError) as ex:
        logger.error(ex)
        return None
    if dict_info is []:
        logger.error("Couldn't parse the provided text file, please make sure it well formatted!")
        return None
    else:
        return dict_info_list

