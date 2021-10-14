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

import json
import logging
import time

import django
from users.models import CustomUser as User
from django.db import transaction

import trackhubs
from trackhubs.constants import DATA_TYPES, FILE_TYPES, VISIBILITY
from trackhubs.hub_check import hub_check
from trackhubs.models import Trackdb, GenomeAssemblyDump
from trackhubs.parser import parse_file_from_url
from trackhubs.tracks_status import fetch_tracks_status, fix_big_data_url

logger = logging.getLogger(__name__)


def get_datatype_filetype_visibility(unique_col, object_name, file_type=False):
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
    return existing_obj


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


def save_datatype_filetype_visibility(name_list, object_name):
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


def save_hub(hub_dict, data_type, current_user):
    """
    Save the hub in MySQL DB if it doesn't exist already
    :param hub_dict: hub dictionary containing all the parsed info
    :param data_type: either specified by the user in the POST request
    or the default one ('genomics')
    :param current_user: the submitter (current user) id
    :returns: the new created hub
    """
    # TODO: Add try expect if the 'hub' or 'url' is empty
    new_hub_obj = trackhubs.models.Hub(
        name=hub_dict['hub'],
        short_label=hub_dict.get('shortLabel'),
        long_label=hub_dict.get('longLabel'),
        url=hub_dict['url'],
        description_url=hub_dict.get('descriptionUrl'),
        email=hub_dict.get('email'),
        data_type=trackhubs.models.DataType.objects.filter(name=data_type).first(),
        owner_id=current_user.id
    )
    new_hub_obj.save()
    return new_hub_obj


def save_trackdb(url, hub, assembly, species):
    """
    Save the genome in MySQL DB  if it doesn't exist already
    :param url: trackdb url
    :param hub: hub object associated with this trackdb
    :param assembly: assembly object associated with this trackdb
    :param species: the species associated with this trackdb
    :returns: either the existing trackdb or the new created one
    """
    existing_trackdb_obj = trackhubs.models.Trackdb.objects.filter(source_url=url).first()
    if existing_trackdb_obj:
        trackdb_obj = existing_trackdb_obj
    else:
        trackdb_obj = trackhubs.models.Trackdb(
            public=True,
            created=int(time.time()),
            updated=int(time.time()),
            assembly=assembly,
            hub=hub,
            species=species,
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
    big_data_url = track_dict.get('bigDataUrl')
    # fix bigDataUrl if it exists
    if big_data_url:
        big_data_full_url = fix_big_data_url(big_data_url, trackdb.source_url)
        try:
            existing_track_obj = trackhubs.models.Track.objects.filter(big_data_url=big_data_full_url).first()
        except KeyError:
            logger.info("bigDataUrl doesn't exist for track: {}".format(track_dict['track']))

    if existing_track_obj:
        return existing_track_obj
    else:
        new_track_obj = trackhubs.models.Track(
            # save name only without 'on' or 'off' settings
            name=get_first_word(track_dict['track']),
            short_label=track_dict.get('shortLabel'),
            long_label=track_dict.get('longLabel'),
            big_data_url=track_dict.get('bigDataUrl'),
            html=track_dict.get('html'),
            parent=None,  # track id will go here later on using add_parent_id() function
            trackdb=trackdb,
            file_type=trackhubs.models.FileType.objects.filter(name=file_type).first(),
            visibility=trackhubs.models.Visibility.objects.filter(name=visibility).first()
        )
        new_track_obj.save()
        return new_track_obj


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
    parent_track = trackhubs.models.Track.objects.filter(name=parent_name_only).first()
    current_track.parent_id = parent_track.track_id
    current_track.save()
    return parent_track


def get_parents(track):
    """
    Get parent and grandparent (if any) of a given track
    :param track: track object
    :returns: the parent and grandparent (if any)
    """

    try:
        parent_track_id = track.parent_id
        parent_track = trackhubs.models.Track.objects.filter(track_id=parent_track_id).first()
    except AttributeError:
        logger.error("Couldn't get the parent of {}".format(track.name))

    try:
        grandparent_track_id = parent_track.parent_id
        grandparent_track = trackhubs.models.Track.objects.filter(track_id=grandparent_track_id).first()
    except AttributeError:
        grandparent_track = None

    return parent_track, grandparent_track


def is_hub_exists(hub_url):
    existing_hub_obj = trackhubs.models.Hub.objects.filter(url=hub_url).first()
    if existing_hub_obj:
        return True
    return False


def get_assembly_info_from_dump(genome_assembly_name):
    """
    Get the assembly information from 'genome_assembly_dump' table
    based on the assemblies submitted by the user
    :param genome_assembly_name: genome assembly name extracted from genomes.txt file
    :returns: assembly info object if found or None otherwise
    """
    assembly_info_from_dump = GenomeAssemblyDump.objects.filter(assembly_name=genome_assembly_name).first()
    assembly_info_from_dump_ucsc_synonym = GenomeAssemblyDump.objects.filter(ucsc_synonym=genome_assembly_name).first()
    if assembly_info_from_dump:
        return assembly_info_from_dump
    elif assembly_info_from_dump_ucsc_synonym:
        return assembly_info_from_dump_ucsc_synonym
    return None


def save_assembly(genome_assembly_name):
    """
    Get the assembly information from 'genome_assembly_dump' table
    based on the assemblies submitted by the user
    :param genome_assembly_name: genome assembly name extracted from genomes.txt file
    :returns: assembly info object if found or None otherwise
    """
    assembly_info_from_dump = get_assembly_info_from_dump(genome_assembly_name)
    existing_assembly_obj = trackhubs.models.Assembly.objects.filter(name=assembly_info_from_dump.assembly_name).first()

    if existing_assembly_obj:
        return existing_assembly_obj
    else:
        new_assembly_obj = trackhubs.models.Assembly(
            accession=assembly_info_from_dump.accession_with_version,
            name=assembly_info_from_dump.assembly_name,
            long_name=assembly_info_from_dump.assembly_name,
            ucsc_synonym=assembly_info_from_dump.ucsc_synonym
        )
        new_assembly_obj.save()
        return new_assembly_obj


def save_species(genome_assembly_name):
    """
    Save species using the provided genome assembly information from the submitted hub
    along with the data stored in 'genome_assembly_dump' table
    :param genomes_info: genomes information extracted from genomes.txt file
    :returns: either species object or, if it's not found or/and cannot be created it
    returns an error message
    TODO: make sure it loops through all species in genome.txt
    """
    assembly_info_from_dump = get_assembly_info_from_dump(genome_assembly_name)

    if assembly_info_from_dump is None:
        return {"error": "Assembly '{}' doesn't exist".format(genome_assembly_name)}

    try:
        existing_species_obj = trackhubs.models.Species.objects.filter(taxon_id=assembly_info_from_dump.tax_id).first()
        if existing_species_obj:
            return existing_species_obj
        else:
            new_species = trackhubs.models.Species(
                taxon_id=assembly_info_from_dump.tax_id,
                scientific_name=assembly_info_from_dump.scientific_name
            )
            new_species.save()
            return new_species
    except django.db.utils.OperationalError:
        logger.exception('Error trying to connect to the database')


def save_and_update_document(hub_url, data_type, current_user):
    """
    Save everything in MySQL DB then Elasticsearch and
    update both after constructing the required objects
    :param hub_url: the hub url provided by the submitter
    :param data_type: the data type provided by the user (if any, default is 'genomics')
    :param current_user: the submitter (current user) id
    :returns: the hub information if the submission was successful otherwise it returns an error
    """
    base_url = hub_url[:hub_url.rfind('/')]

    # TODO: this three lines should be moved somewhere else where they are executed only once
    # See Providing initial data for models: https://docs.djangoproject.com/en/2.2/howto/initial-data/
    save_datatype_filetype_visibility(DATA_TYPES, trackhubs.models.DataType)
    save_datatype_filetype_visibility(FILE_TYPES, trackhubs.models.FileType)
    save_datatype_filetype_visibility(VISIBILITY, trackhubs.models.Visibility)

    # Verification steps
    # Before we submit the hub we make sure that it doesn't exist already
    if is_hub_exists(hub_url):
        original_owner_id = trackhubs.models.Hub.objects.filter(url=hub_url).first().owner_id
        if original_owner_id == current_user.id:
            return {'error': 'The Hub is already submitted, please delete it before resubmitting it again'}
        original_owner_email = User.objects.filter(id=original_owner_id).first().email
        return {"error": "This hub is already submitted by a different user (the original submitter's email: {})".format(original_owner_email)}

    # run the USCS hubCheck tool found in kent tools on the submitted hub
    hub_check_result = hub_check(hub_url)
    if 'error' in hub_check_result.keys():
        return hub_check_result

    hub_info_array = parse_file_from_url(hub_url, is_hub=True)

    if hub_info_array:
        hub_info = hub_info_array[0]
        logger.debug("hub_info: {}".format(json.dumps(hub_info, indent=4)))

        # check if the user provides the data type, default is 'genomics'
        if data_type:
            data_type = data_type.lower()
            if data_type not in DATA_TYPES:
                return {"Error": "'{}' isn't a valid data type, the valid ones are: '{}'".format(data_type, ", ".join(DATA_TYPES))}
        else:
            data_type = 'genomics'

        genome_url = base_url + '/' + hub_info['genomesFile']
        genomes_trackdbs_info = parse_file_from_url(genome_url, is_genome=True)
        logger.debug("genomes_trackdbs_info: {}".format(json.dumps(genomes_trackdbs_info, indent=4)))

        hub_obj = save_hub(hub_info, data_type, current_user)

        for genome_trackdb in genomes_trackdbs_info:
            logger.debug("genomes_trackdb: {}".format(json.dumps(genome_trackdb, indent=4)))

            error_or_species_obj = save_species(genome_trackdb['genome'])
            if not isinstance(error_or_species_obj, trackhubs.models.Species):
                # delete the hub from MySQL
                hub_obj.delete()
                # An error message is shown if the returned result is not an instance of Species
                return error_or_species_obj

            # we got the assembly_name from genomes_trackdb['genome']
            assembly_obj = save_assembly(genome_trackdb['genome'])

            # Save the initial data
            trackdb_url = base_url + '/' + genome_trackdb['trackDb']
            trackdb_obj = save_trackdb(trackdb_url, hub_obj, assembly_obj, error_or_species_obj)

            trackdbs_info = parse_file_from_url(trackdb_url, is_trackdb=True)
            # logger.debug("trackdbs_info: {}".format(json.dumps(trackdbs_info, indent=4)))

            tracks_status = fetch_tracks_status(trackdbs_info, trackdb_url)

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
                        file_type = get_datatype_filetype_visibility(track['type'], trackhubs.models.FileType, file_type=True).name
                    if 'visibility' in track:
                        visibility = get_datatype_filetype_visibility(track['visibility'], trackhubs.models.Visibility).name

                    track_obj = get_obj_if_exist(track['track'], trackhubs.models.Track)
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
            current_trackdb.configuration = trackdb_configuration
            current_trackdb.status = tracks_status
            current_trackdb.data = trackdb_data
            current_trackdb.save()
            # Update Elasticsearch trackdb document
            trackdb_obj.update_trackdb_document(hub_obj, trackdb_data, trackdb_configuration, tracks_status)

        return {'success': 'The hub is submitted successfully'}

    return None


