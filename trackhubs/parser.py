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

# from thr.settings import BASE_DIR
import time

from django.db import connection
from elasticsearch_dsl import connections

from trackhubs.models import Hub, Species, DataType, Trackdb, FileType, Visibility, Genome, Assembly, Track

BDIR = 'samples/JASPAR_TFBS/'
hub_file = BDIR + 'hub.txt'  # BASE_DIR / 'samples/JASPERT_TFBS/hub.txt'


def is_row_exists(obj_class, col_name, col_value):
    if obj_class.objects.filter(**{col_name: col_value}).exists():
        return True
    return False


def is_db_table_exists(table_name):
    return table_name in connection.introspection.table_names()


def parse_file(filepath):
    """
    Parse the hub.txt, genomes.txt and trackdb.txt files
    :param filepath: the file path
    :returns: an array of dictionaries, each dictionary contains one object
    either hub, genome or track
    """
    count = 0
    dicts_info = [{'url': filepath}]
    try:
        with open(filepath) as fp:
            line = fp.readline()
            while line:
                splitted_line = line.rstrip('\n').split(' ', 1)
                if '' in splitted_line:
                    # new line marks a new genomes/tracks/supertracks etc
                    # in this case we create a new dictionary where we store the new element
                    dicts_info.append({'url': filepath})
                    count += 1
                    line = fp.readline()
                    continue

                dicts_info[count][splitted_line[0]] = splitted_line[1]
                line = fp.readline()
    except IOError:
        print('WARNING: The file ' + filepath + ' doesn\'t exist')
    return dicts_info


def save_data_type():
    # TODO: Remove species
    if not Species.objects.filter(taxon_id=9606).exists():
        sp = Species(
            taxon_id=9606,
            scientific_name='Homo sapiens'
        )
        sp.save()

    data_type_list = ['genomics', 'proteomics', 'epigenomics', 'transcriptomics']
    data_type_list_obj = []
    for dt in data_type_list:
        if not DataType.objects.filter(name=dt).exists():
            dt_obj = DataType(name=dt)
            data_type_list_obj.append(dt_obj)

    DataType.objects.bulk_create(data_type_list_obj)


def save_file_type(file_type_name):
    # trim the type in case we have extra info e.g 'type bigBed 6 +'
    file_type_name = file_type_name.rstrip('\n').split(' ')[0]  # e.g ['bigBed', '6', '+']
    existing_file_type_obj = FileType.objects.filter(name=file_type_name).first()
    if existing_file_type_obj:
        return existing_file_type_obj
    else:
        new_file_type_obj = FileType(
            name=file_type_name
        )
        new_file_type_obj.save()
        return new_file_type_obj


def save_visibility(visibility_name):
    existing_visibility_obj = Visibility.objects.filter(name=visibility_name).first()
    if existing_visibility_obj:
        return existing_visibility_obj
    else:
        new_visibility_obj = Visibility(
            name=visibility_name
        )
        new_visibility_obj.save()
        return new_visibility_obj


def save_hub(hub_dict, species=00, data_type=00):
    # if db_table_exists('hub'):
    existing_hub_obj = Hub.objects.filter(url=hub_dict['url']).first()
    if existing_hub_obj:
        return existing_hub_obj
    else:
        new_hub_obj = Hub(
            name=hub_dict['hub'],
            short_label=hub_dict['shortLabel'],
            long_label=hub_dict['longLabel'],
            url=hub_dict['url'],
            description_url=hub_dict['descriptionUrl'],
            email=hub_dict['email'],
            species_id=1,
            data_type_id=1
        )
        new_hub_obj.save()
        return new_hub_obj


def save_genome(genome_dict, hub):
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
    existing_assembly_obj = Assembly.objects.filter(name=assembly_dict['name']).first()
    if existing_assembly_obj:
        return existing_assembly_obj
    else:
        new_assembly_obj = Assembly(
            accession='GCA_000001735.1',
            name=assembly_dict['name'],
            long_name='',
            synonyms='',
            genome=genome
        )
        new_assembly_obj.save()
        return new_assembly_obj


def save_trackdb(url, hub, genome, assembly):
    existing_trackdb_obj = Trackdb.objects.filter(source_url=url).first()
    if existing_trackdb_obj:
        trackdb_obj = existing_trackdb_obj
    else:
        trackdb_obj = Trackdb(
            public=True,
            # 'description'
            # 'version',
            created=time.time(),
            updated=time.time(),
            assembly=assembly,
            # type=dt,
            hub=hub,
            # genome_id=1,
            # configurations=cf,
            genome=genome,
            source_url=url,
            source_checksum='',
            status_message='okokok'
        )
        trackdb_obj.save()

    return trackdb_obj


def save_track(track_dict, trackdb, file_type, visibility):
    existing_track_obj = Track.objects.filter(big_data_url=track_dict['bigDataUrl']).first()
    if existing_track_obj:
        return existing_track_obj
    else:
        new_track_obj = Track(
            name=track_dict['track'],
            short_label=track_dict['shortLabel'],
            long_label=track_dict['longLabel'],
            big_data_url=track_dict['bigDataUrl'],
            html=track_dict['html'],
            parent=None,  # track
            trackdb=trackdb,
            file_type=file_type,
            visibility=visibility
        )
        new_track_obj.save()
        return new_track_obj


def update_trackdb_index(trackdb, file_type, trackdb_data):
    print("#### Updating trackdb id: ", trackdb.trackdb_id)
    es = connections.Elasticsearch()
    es.update(
        index='trackhubs',
        doc_type='doc',
        id=trackdb.trackdb_id,
        refresh=True,
        body={'doc':
            {
                'file_type': {
                    file_type.name: -1
                },
                'data': trackdb_data,
                'updated': time.time()
            }
        }
    )


def get_trackdb_data(track):
    pass


def save_all(hub_filepath):
    # print(is_row_exists(Species, 'taxon_id', 9605))

    save_data_type()  # if is_db_table_exists('species') else 'TABLE NEST PAS LA!!'

    hub_info = parse_file(hub_filepath)[0]
    hub_obj = save_hub(hub_info)

    genomes_info = parse_file(BDIR + hub_info['genomesFile'])

    for genome in genomes_info:
        genome_obj = save_genome(genome, hub_obj)

        assembly_info = {'name': genome['genome']}
        assembly_obj = save_assembly(assembly_info, genome_obj)

        # Save the initial data
        trackdb_obj = save_trackdb(BDIR + genome['trackDb'], hub_obj, genome_obj, assembly_obj)

        trackdbs_info = parse_file(BDIR + genome['trackDb'])
        # print('track_info ---> ', tracks_info)

        trackdb_data = []
        for track in trackdbs_info:
            # get the file type and visibility
            file_type = save_file_type(track['type'])
            visibility = save_visibility(track['visibility'])

            if 'track' in track:
                track_obj = save_track(track, trackdb_obj, file_type, visibility)

            trackdb_data.append(
                {
                    'id': track_obj.name,
                    'name': track_obj.long_label
                }
            )

            update_trackdb_index(trackdb_obj, file_type, trackdb_data)
            # update MySQL
            current_trackdb = Trackdb.objects.get(trackdb_id=trackdb_obj.trackdb_id)
            current_trackdb.configurations = trackdb_data
            current_trackdb.save()


save_all(hub_file)
