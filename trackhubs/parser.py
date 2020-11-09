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
import json
import urllib.request

import django
import elasticsearch
from elasticsearch_dsl import connections

from trackhubs.models import Hub, Species, DataType, Trackdb, FileType, Visibility, Genome, Assembly, Track
from .constants import DATA_TYPES, FILE_TYPES, VISIBILITY

logger = logging.getLogger(__name__)

# This hub is quite big
# hub_url = 'http://ftp.ebi.ac.uk/pub/databases/ensembl/encode/integration_data_jan2011/hub.txt'
hub_url = 'https://data.broadinstitute.org/compbio1/PhyloCSFtracks/trackHub/hub.txt'
# hub_url = 'ftp://ftp.vectorbase.org/public_data/rnaseq_alignments/hubs/aedes_aegypti/VBRNAseq_group_SRP039093/hub.txt'
# hub_url = 'http://urgi.versailles.inra.fr/repetdb/repetdb_trackhubs/repetdb_Melampsora_larici-populina_98AG31_v1.0/hub.txt'


def parse_file_from_url(url, is_hub=False, is_genome=False, is_trackdb=False):
    """
    Parse the hub.txt, genomes.txt and trackdb.txt files from given hub url
    :param url: hub,genomes or trackdb url
    :param is_hub: is set to true if we are parsing a hub
    :param is_genome: is set to true if we are parsing genomes
    :param is_trackdb: is set to true if we are parsing trackdb
    :returns: an array of dictionaries, each dictionary contains one object
    either hub, genome or track
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

            splitted_line = line.rstrip('\n').split(' ', 1)
            key = splitted_line[0].strip()
            dict_info[key] = splitted_line[1]

        # This part is ugly, but it's the only way I found to make sure the last
        # element is added to the returned dict_info_list (in case there is no new line
        # at the end of the parsed file)
        # TODO: find a better way to detect the EOF
        if (is_hub and 'hub' in dict_info and not any(d.get('hub') == dict_info.get('hub') for d in dict_info_list)) or \
                (is_genome and 'genome' in dict_info and not any(d.get('genome') == dict_info.get('genome') for d in dict_info_list)) or \
                (is_trackdb and 'track' in dict_info and not any(d.get('track') == dict_info.get('track') for d in dict_info_list)):
            dict_info.update({'url': url})
            dict_info_list.append(dict_info)

    except (IOError, urllib.error.HTTPError, urllib.error.URLError, ValueError, AttributeError) as ex:
        logger.error(ex)
        return None
    if dict_info is []:
        logger.error("Couldn't parse the provided text file, please make sure it well formatted!")
    else:
        return dict_info_list


def save_fake_species():
    """
    Save fake species, this will be replaced with a proper function later
    """
    # TODO: Replace this with a proper one
    try:
        if not Species.objects.filter(taxon_id=9606).exists():
            sp = Species(
                taxon_id=9606,
                scientific_name='Homo sapiens'
            )
            sp.save()
    except django.db.utils.OperationalError:
        logger.exception('Error trying to connect to Elasticsearch')


def get_obj(unique_col, object_name, file_type=False):
    """
    Get object (can be DataType, FileType or Visibility) by name
    Create one if it doesn't exist?
    TODO: merge it with get_obj_if_exist() by adding create_if_not_exist param
    :param unique_col: hub,genomes or trackdb url
    :param object_name: can be DataType, FileType or Visibility
    :param file_type: is set to true if we are parsing genomes
    :returns: either the existing object or the new created one
    """
    if file_type:
        # trim the type in case we have extra info e.g 'type bigBed 6 +'
        unique_col = get_first_word(unique_col)

    existing_obj = object_name.objects.filter(name=unique_col).first()
    if existing_obj:
        return existing_obj
    else:
        new_obj = object_name(
            name=unique_col
        )
        new_obj.save()
        return new_obj


def get_obj_if_exist(unique_col, object_name, file_type=False):
    """
    Returns the object if it exists otherwise it returns None
    :param unique_col: hub,genomes or trackdb url
    :param object_name: can be DataType, FileType or Visibility
    :param file_type: is set to true if we are parsing genomes
    :returns: either the existing object or the new created one
    """
    if file_type:
        # trim the type in case we have extra info e.g 'type bigBed 6 +'
        unique_col = get_first_word(unique_col)

    existing_obj = object_name.objects.filter(name=unique_col).first()
    if existing_obj:
        return existing_obj
    else:
        return None


def save_constant_data(name_list, object_name):
    """
    Save all constants rows of DataType, FileType and Visibility
    in their corresponding table
    name_list: list of the values to be stored
    object_name: either DataType, FileType or Visibility
    TODO: this function should be executed once just after creating the database
    """
    name_list_obj = []
    for name in name_list:
        if not object_name.objects.filter(name=name).exists():
            obj = object_name(name=name)
            name_list_obj.append(obj)

    object_name.objects.bulk_create(name_list_obj)


def save_hub(hub_dict, data_type, species=00):
    """
    Save the hub in MySQL DB if it doesn't exist already
    :param hub_dict: hub dictionary containing all the parsed info
    :param data_type: either specified by the user in the POST request
    or the default one ('genomics')
    :param species: the species associated with this hub
    # TODO: work on adding species
    :returns: either the existing hub or the new created one
    """
    existing_hub_obj = Hub.objects.filter(url=hub_dict['url']).first()
    if existing_hub_obj:
        return existing_hub_obj
    else:
        # TODO: Add try expect if the 'hub' or 'url' is empty
        new_hub_obj = Hub(
            name=hub_dict['hub'],
            short_label=hub_dict.get('shortLabel'),
            long_label=hub_dict.get('longLabel'),
            url=hub_dict['url'],
            description_url=hub_dict.get('descriptionUrl'),
            email=hub_dict.get('email'),
            data_type=DataType.objects.filter(name=data_type).first(),
            species_id=1
        )
        new_hub_obj.save()
        return new_hub_obj


def save_genome(genome_dict, hub):
    """
    Save the genome in MySQL DB  if it doesn't exist already
    :param genome_dict: genome dictionary containing all the parsed info
    :param hub: hub object associated with this genome
    :returns: either the existing genome or the new created one
    """
    existing_genome_obj = Genome.objects.filter(name=genome_dict['genome']).first()
    if existing_genome_obj:
        return existing_genome_obj
    else:
        new_genome_obj = Genome(
            name=genome_dict['genome'],
            trackdb_location=genome_dict['trackDb'],
            hub=hub
        )
        new_genome_obj.save()
        return new_genome_obj


def save_assembly(assembly_dict, genome):
    """
    Save the genome in MySQL DB  if it doesn't exist already
    :param assembly_dict: assembly dictionary containing all the parsed info
    :param genome: genome object associated with this assembly
    :returns: either the existing assembly or the new created one
    """
    existing_assembly_obj = Assembly.objects.filter(name=assembly_dict['name']).first()
    if existing_assembly_obj:
        return existing_assembly_obj
    else:
        new_assembly_obj = Assembly(
            accession='accession_goes_here',
            name=assembly_dict['name'],
            long_name='',
            synonyms='',
            genome=genome
        )
        new_assembly_obj.save()
        return new_assembly_obj


def save_trackdb(url, hub, genome, assembly):
    """
    Save the genome in MySQL DB  if it doesn't exist already
    :param url: trackdb url
    :param hub: hub object associated with this trackdb
    :param genome: genome object associated with this trackdb
    :param assembly: assembly object associated with this trackdb
    :returns: either the existing trackdb or the new created one
    """
    existing_trackdb_obj = Trackdb.objects.filter(source_url=url).first()
    if existing_trackdb_obj:
        trackdb_obj = existing_trackdb_obj
    else:
        trackdb_obj = Trackdb(
            public=True,
            created=int(time.time()),
            updated=int(time.time()),
            assembly=assembly,
            hub=hub,
            genome=genome,
            source_url=url
        )
        trackdb_obj.save()

    return trackdb_obj


def save_track(track_dict, trackdb, file_type, visibility):
    """
    Save the track in MySQL DB  if it doesn't exist already
    :param track_dict: track dictionary containing all the parsed info
    :param trackdb: trackdb object associated with this track
    :param file_type: file type string associated with this track
    :param visibility: visibility string associated with this track (default: 'hide')
    :returns: either the existing track or the new created one
    """
    existing_track_obj = None
    try:
        existing_track_obj = Track.objects.filter(big_data_url=track_dict['bigDataUrl']).first()
    except KeyError:
        logger.info("bigDataUrl doesn't exist for track: {}".format(track_dict['track']))

    if existing_track_obj:
        return existing_track_obj
    else:
        new_track_obj = Track(
            # save name only without 'on' or 'off' settings
            name=get_first_word(track_dict['track']),
            short_label=track_dict.get('shortLabel'),
            long_label=track_dict.get('longLabel'),
            big_data_url=track_dict.get('bigDataUrl'),
            html=track_dict.get('html'),
            parent=None,  # track
            trackdb=trackdb,
            file_type=FileType.objects.filter(name=file_type).first(),
            visibility=Visibility.objects.filter(name=visibility).first()
        )
        new_track_obj.save()
        return new_track_obj


def update_trackdb_document(trackdb, file_type, trackdb_data, trackdb_configuration, hub):
    """
    Update trackdb document in Elascticsearch with the additional data provided
    :param trackdb: trackdb object to be updated
    :param file_type: file type string associated with this track
    # TODO: write the proper query, file_type param will be removed
    :param trackdb_data: data array that will be added to the trackdb document
    :param trackdb_configuration: configuration object that will be added to the trackdb document
    :param hub: hub object associated with this trackdb
    # TODO: handle exceptions
    """
    try:
        es = connections.Elasticsearch(timeout=30)
        es.update(
            index='trackhubs',
            doc_type='doc',
            id=trackdb.trackdb_id,
            refresh=True,
            body={
                'doc': {
                    'file_type': {
                        # TODO: write a proper query/function (e.g get_file_type_count(trackdb))
                        file_type: FileType.objects.filter(name=file_type).count()
                    },
                    'data': trackdb_data,
                    'updated': int(time.time()),
                    'source': {
                        'url': trackdb.source_url,
                        'checksum': ''
                    },
                    # Get the data type based on the hub info
                    'type': Hub.objects.filter(data_type_id=hub.data_type_id)
                        .values('data_type__name').first()
                        .get('data_type__name'),
                    'configuration': trackdb_configuration
                }
            }
        )
        logger.info("Trackdb id {} is updated successfully".format(trackdb.trackdb_id))

    except elasticsearch.exceptions.ConnectionError:
        logger.exception("There was an error while trying to connect to Elasticsearch. "
              "Please make sure ES service is running and configured properly!")


def get_first_word(tabbed_info):
    """
    Get the first word in a sentence, this is useful when
    we want to get file type, for instance,
    >> get_first_word('bigBed 6 +') will return 'bigBed'
    :param tabbed_info: the string (e.g. 'bigBed 6 +')
    :returns: the first word in the string
    """
    return tabbed_info.rstrip('\n').split(' ')[0]  # e.g ['bigBed', '6', '+']


def add_parent_id(parent_name, current_track):
    """
    Update track's parent id if there is any
    :param parent_name: extracted from the track info
    :param current_track: current track object
    """
    # get the track parent name only without extra configuration
    # e.g. 'uniformDnasePeaks off' becomes 'uniformDnasePeaks'
    parent_name_only = get_first_word(parent_name).strip()
    # IDEA: DRY create get where function
    parent_track = Track.objects.filter(name=parent_name_only).first()
    current_track.parent_id = parent_track.track_id
    current_track.save()
    return parent_name_only


def get_parents(track):
    """
    Get parent and grandparent (if any) of a given track
    :param track: track object
    :returns: the parent and grandparent (if any)
    """

    try:
        parent_track_id = track.parent_id
        parent_track = Track.objects.filter(track_id=parent_track_id).first()
    except AttributeError:
        logger.error("Couldn't get the parent of {}".format(track.name))

    try:
        grandparent_track_id = parent_track.parent_id
        grandparent_track = Track.objects.filter(track_id=grandparent_track_id).first()
    except AttributeError:
        grandparent_track = None

    return parent_track, grandparent_track


def save_and_update_document(hub_url):
    """
    Save everything in MySQL DB then Elasticsearch and
    update both after constructing the required objects
    :param hub_url: the hub url provided by the submitter
    """
    base_url = hub_url[:hub_url.rfind('/')]
    save_fake_species()

    save_constant_data(DATA_TYPES, DataType)
    save_constant_data(FILE_TYPES, FileType)
    save_constant_data(VISIBILITY, Visibility)

    hub_info = parse_file_from_url(hub_url, is_hub=True)[0]

    logger.debug("hub_info: {}".format(json.dumps(hub_info, indent=4)))

    data_type = 'epigenomics'
    hub_obj = save_hub(hub_info, data_type)

    genomes_trackdbs_info = parse_file_from_url(base_url + '/' + hub_info['genomesFile'], is_genome=True)
    logger.debug("genomes_trackdbs_info: {}".format(json.dumps(genomes_trackdbs_info, indent=4)))

    for genomes_trackdb in genomes_trackdbs_info:
        # logger.debug("genomes_trackdb: {}".format(json.dumps(genomes_trackdb, indent=4)))

        genome_obj = save_genome(genomes_trackdb, hub_obj)

        assembly_info = {'name': genomes_trackdb['genome']}
        assembly_obj = save_assembly(assembly_info, genome_obj)

        # Save the initial data
        trackdb_obj = save_trackdb(base_url + '/' + genomes_trackdb['trackDb'], hub_obj, genome_obj, assembly_obj)

        trackdbs_info = parse_file_from_url(base_url + '/' + genomes_trackdb['trackDb'], is_trackdb=True)
        # logger.debug("trackdbs_info: {}".format(json.dumps(trackdbs_info, indent=4)))

        trackdb_data = []
        trackdb_configuration = {}
        for track in trackdbs_info:
            # logger.debug("track: {}".format(json.dumps(track, indent=4)))

            if 'track' in track:
                # default value
                visibility = 'hide'
                # get the file type and visibility
                # TODO: if file_type in FILE_TYPES Good, Else Error
                if 'type' in track:
                    file_type = get_obj(track['type'], FileType, file_type=True).name
                if 'visibility' in track:
                    visibility = get_obj(track['visibility'], Visibility).name

                track_obj = get_obj_if_exist(track['track'], Track)
                if not track_obj:
                    track_obj = save_track(track, trackdb_obj, file_type, visibility)

                trackdb_data.append(
                    {
                        'id': track_obj.name,
                        'name': track_obj.long_label
                    }
                )

                # if the track is parent we prepare the configuration object
                if any(k in track for k in ('compositeTrack', 'superTrack', 'container')):
                    # logger.debug("'{}' is parent".format(track['track']))
                    trackdb_configuration[track['track']] = track
                    trackdb_configuration[track['track']].pop('url', None)

                # if the track is a child, add the parent id and update
                # the configuration to include the current track
                if 'parent' in track:
                    add_parent_id(track['parent'], track_obj)
                    parent_track_obj, grandparent_track_obj = get_parents(track_obj)

                    if grandparent_track_obj is None:  # Then we are in the first level (subtrack)
                        if 'members' not in trackdb_configuration[parent_track_obj.name]:
                            trackdb_configuration[parent_track_obj.name].update({
                                'members': {
                                    track['track']: track
                                }
                            })
                        else:
                            trackdb_configuration[parent_track_obj.name]['members'].update({
                                track['track']: track
                            })

                    else:  # we are in the second level (subsubtrack)
                        if 'members' not in trackdb_configuration[grandparent_track_obj.name]['members'][parent_track_obj.name]:
                            trackdb_configuration[grandparent_track_obj.name]['members'][parent_track_obj.name].update({
                                'members': {
                                    track['track']: track
                                }
                            })
                        else:
                            trackdb_configuration[grandparent_track_obj.name]['members'][parent_track_obj.name]['members'].update({
                                track['track']: track
                            })

        # update MySQL
        current_trackdb = Trackdb.objects.get(trackdb_id=trackdb_obj.trackdb_id)
        current_trackdb.configurations = trackdb_configuration
        current_trackdb.save()
        # Update Elasticsearch trackdb document
        update_trackdb_document(trackdb_obj, file_type, trackdb_data, trackdb_configuration, hub_obj)


# save_and_update_document(hub_url)

# TODO: add delete_hub() etc

