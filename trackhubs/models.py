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
import re
import sys
from datetime import datetime
import logging
import time
import hashlib

import requests
from django.conf import settings
from django.db import models
from django.db.models import Count
from django_elasticsearch_dsl_drf.wrappers import dict_to_obj
from django_mysql.models import JSONField
import elasticsearch
from elasticsearch_dsl import connections

from thr.settings import ELASTICSEARCH_DSL
from users.models import CustomUser as User
import trackhubs
from trackhubs.utils import remove_html_tags
logger = logging.getLogger(__name__)


class Species(models.Model):
    class Meta:
        db_table = "species"

    id = models.AutoField(primary_key=True)
    taxon_id = models.IntegerField()
    scientific_name = models.CharField(max_length=255, null=True)
    common_name = models.CharField(max_length=255, null=True)


class DataType(models.Model):
    class Meta:
        db_table = "data_type"

    data_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, default="genomics")


class FileType(models.Model):
    class Meta:
        db_table = "file_type"

    file_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    settings = models.JSONField(null=True)


class Visibility(models.Model):
    class Meta:
        db_table = "visibility"

    visibility_id = models.AutoField(primary_key=True)
    name = models.CharField(default="hide", max_length=45)


class Hub(models.Model):
    class Meta:
        db_table = "hub"

    hub_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    shortLabel = models.TextField(blank=True, null=True)
    longLabel = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=255)
    description_url = models.URLField(null=True)
    email = models.EmailField(null=True)
    data_type = models.ForeignKey(DataType, on_delete=models.CASCADE)
    assembly_hub = models.BooleanField(default=False)
    # TODO: make sure that if the owner is deleted, the hubs are deleted too
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def get_owner(self):
        # return User.objects.filter(id=self.owner_id)
        return User.objects.values_list('username', flat=True).get(id=self.owner_id)

    def count_trackdbs_in_hub(self):
        return Trackdb.objects.filter(hub_id=self.hub_id).count()

    def get_trackdbs_list_from_hub(self):
        """
        Create trackdbs list that is used in GET /api/trackhub
        """
        trackdbs_obj = Trackdb.objects.filter(hub_id=self.hub_id)
        trackdbs_list = []
        for trackdb in trackdbs_obj:
            trackdbs_list.append(
                {
                    'trackdb_id': trackdb.trackdb_id,
                    'species': str(Species.objects.get(taxon_id=trackdb.species.taxon_id).taxon_id),
                    'assembly': Assembly.objects.get(assembly_id=trackdb.assembly.assembly_id).name,
                    'uri': 'https://www.new-trackhubregistry-url.org/user/view_trackhub_status/{}'.format(
                        trackdb.trackdb_id),
                    'schema': trackdb.version,
                    'created': datetime.utcfromtimestamp(trackdb.created).strftime('%Y-%m-%d %H:%M:%S'),
                    'updated': datetime.utcfromtimestamp(trackdb.updated).strftime('%Y-%m-%d %H:%M:%S') if trackdb.updated else None,
                    'status': trackdb.status,
                }
            )
        return trackdbs_list

    def get_trackdbs_full_list_from_hub(self):
        """
        Create trackdbs list that is used in GET /api/trackhub/:id
        it doesn't make much sense to have /api/trackhub and /api/trackhub/:id
        with different structures but it part of the requirement to keep
        the current JSON structure as it is
        """
        trackdbs_obj = Trackdb.objects.filter(hub_id=self.hub_id)
        trackdbs_list = []
        for trackdb in trackdbs_obj:
            trackdbs_list.append(
                {
                    'trackdb_id': trackdb.trackdb_id,
                    'species': {
                        'scientific_name': Species.objects.get(taxon_id=trackdb.species.taxon_id).scientific_name,
                        'tax_id': str(Species.objects.get(taxon_id=trackdb.species.taxon_id).taxon_id),
                        'common_name': Species.objects.get(taxon_id=trackdb.species.taxon_id).common_name,
                    },
                    'assembly': {
                        'name': Assembly.objects.get(assembly_id=trackdb.assembly.assembly_id).name,
                        'long_name': Assembly.objects.get(assembly_id=trackdb.assembly.assembly_id).long_name,
                        'accession': Assembly.objects.get(assembly_id=trackdb.assembly.assembly_id).accession,
                        'synonyms': Assembly.objects.get(assembly_id=trackdb.assembly.assembly_id).ucsc_synonym
                    },
                    'uri': 'https://www.new-trackhubregistry-url.org/user/view_trackhub_status/{}'.format(
                        trackdb.trackdb_id),
                }
            )
        return trackdbs_list

    def get_trackdbs_ids_from_hub(self):
        """
        Get all the trackdbs id belonging to the hub
        This function is used to delete trackdbs document from Elasticsearch
        since trackdbs in MySQL have the same ids in the Elasticsearch index
        """
        trackdbs_ids_list = Trackdb.objects.filter(hub_id=self.hub_id).values_list('pk', flat=True)
        logger.debug("IDs of all the trackdbs that will be deleted: {}".format(trackdbs_ids_list))
        return trackdbs_ids_list


class Assembly(models.Model):
    class Meta:
        db_table = "assembly"

    assembly_id = models.AutoField(primary_key=True)
    accession = models.CharField(max_length=255)
    name = models.CharField(max_length=255, null=True)
    long_name = models.CharField(max_length=255, null=True)
    ucsc_synonym = models.CharField(max_length=255, null=True)


class Trackdb(models.Model):
    class Meta:
        db_table = "trackdb"

    trackdb_id = models.AutoField(primary_key=True)
    public = models.BooleanField(default=False)
    description = models.TextField(null=True)
    version = models.CharField(default="v1.0", max_length=10)
    created = models.IntegerField(default=int(time.time()))
    updated = models.IntegerField(null=True)
    configuration = models.JSONField(null=True)
    data = models.JSONField(null=True)
    status = models.JSONField(null=True)
    browser_links = models.JSONField(null=True)
    source_url = models.CharField(max_length=255, null=True)
    source_checksum = models.CharField(max_length=255, null=True)
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE)
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE)
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    # is_archived may be needed in the future
    is_archived = models.BooleanField(default=False)


    @property
    def data_type_indexing(self):
        """
        Data type for indexing.
        Used in Elasticsearch indexing.
        """
        return self.hub.data_type.name

    @property
    def species_indexing(self):
        """species data (nested) for indexing.

        Example:

        >>> mapping = {
        >>>     'species': {
        >>>         'taxon_id': '9823',
        >>>         'scientific_name': 'Sus scrofa',
        >>>         'common_name': 'pig',
        >>>     }
        >>> }

        :return:
        """
        wrapper = dict_to_obj({
            'taxon_id': self.species.taxon_id,
            'scientific_name': self.species.scientific_name,
            'common_name': self.species.common_name,
        })

        return wrapper

    @property
    def assembly_indexing(self):
        """assembly data (nested) for indexing.

        Example:

        >>> mapping = {
        >>>     'assembly': {
        >>>         'accession': 'GCA_000150955.2',
        >>>         'name': 'ASM15095v2',
        >>>         'long_name': 'ASM15095v2 assembly for Phaeodactylum tricornutum CCAP 1055/1',
        >>>         'ucsc_synonym': null,
        >>>     }
        >>> }

        :return:
        """
        wrapper = dict_to_obj({
            'accession': self.assembly.accession,
            'name': self.assembly.name,
            'long_name': self.assembly.long_name,
            'ucsc_synonym': self.assembly.ucsc_synonym,
        })

        return wrapper

    def count_tracks_in_trackdb(self):
        return Track.objects.filter(trackdb_id=self.trackdb_id).count()

    def get_hub_from_trackdb(self):
        hub_id = Trackdb.objects.get(trackdb_id=self.trackdb_id).hub_id
        return Hub.objects.get(hub_id=hub_id)

    def get_trackdb_file_type_count(self):
        """
        For a giving trackdb return the file type + count
        e.g file_type_counts_dict = {'bigBed': 20, 'bigWig': 1, 'bed': 1}
        """
        file_type_counts = (
            trackhubs.models
                # where trackdb_id is self
                .Track.objects.filter(trackdb=self)
                # get file_type name
                .values('file_type__name')
                # and count(file_type_id) as count
                .annotate(count=Count('file_type'))
                # excluding big_data_url null values and empty strings
                .exclude(big_data_url__isnull=True)
                .exclude(big_data_url__exact='')
        )
        file_type_counts_dict = {}
        for ft_count in file_type_counts:
            file_type_counts_dict.update({ft_count['file_type__name']: ft_count['count']})

        return file_type_counts_dict

    def generate_browser_links(self):
        """
        Generate browser links in UCSC, Ensembl and VectorBase for the current trackdb
        """
        browser_links = {}
        division = None

        # Get the hub url and short label using hub id in trackdb object
        hub_url_and_short_label = Hub.objects.filter(hub_id=self.hub_id).values('url', 'shortLabel').first()
        hub_url = hub_url_and_short_label['url']
        hub_short_label = hub_url_and_short_label['shortLabel']
        short_label_stripped = remove_html_tags(hub_short_label).strip()  # .replace(' ', '%20')

        # Get the assembly name and ucsc synonym using assembly id in trackdb object
        assembly_name_synonym_accession = Assembly.objects.filter(assembly_id=self.assembly_id).values('name',
                                                                                                          'ucsc_synonym',
                                                                                                          'accession').first()
        assembly_name = assembly_name_synonym_accession['name']
        assembly_ucsc_synonym = assembly_name_synonym_accession['ucsc_synonym']
        assembly_accession = assembly_name_synonym_accession['accession']

        # TODO: add the assembly hub case
        #  see: http://genome.ucsc.edu/goldenPath/help/hubQuickStartAssembly.html
        is_assembly_hub = 0

        # UCSC browser link
        # Provide different links in case it's an assembly hub or an assembly supported by UCSC
        if is_assembly_hub:
            # see http://genome.ucsc.edu/goldenPath/help/hubQuickStartAssembly.html
            browser_links['ucsc'] = "http://genome.ucsc.edu/cgi-bin/hgHubConnect?hgHub_do_redirect=on&hgHubConnect" \
                                    ".remakeTrackHub=on&hgHub_do_firstDb=1&hubUrl={}".format(hub_url)
        elif assembly_ucsc_synonym:
            # assembly supported by UCSC
            browser_links['ucsc'] = "http://genome.ucsc.edu/cgi-bin/hgHubConnect?db={}&hubUrl={" \
                                    "}&hgHub_do_redirect=on&hgHubConnect.remakeTrackHub=on".format(
                assembly_ucsc_synonym,
                hub_url);

        # Biodalliance embeddable browser link
        # NOTE: support for only human assemblies, i.e. those for which we can
        # fetch 2bit assembly data from the biodalliance server
        if assembly_ucsc_synonym in ['hg19', 'hg38', 'mm10'] and not hub_url.startswith('ftp'):
            browser_links['biodalliance'] = "/biodalliance/view?assembly={}&name={}&url={}" \
                .format(assembly_ucsc_synonym, hub_short_label.strip(), hub_url)

        # Get the species scientific name using species id in trackdb object
        species_scientific_name = Species.objects.filter(id=self.species_id).values('scientific_name').first().get(
            'scientific_name')
        species_scientific_name = species_scientific_name.replace(' ', '_')

        # First the special cases:
        # - human (grch38.* -> www, grch37.* -> grch37)
        # - mouse (only grcm38.* supported -> www)
        # - fruitfly (Release 6 up-to-date, Release 5 from Dec 2014 backward)
        # - rat (Rnor_6.0 up-to-date, Rnor_5.0 from Mar 2015 backward)
        # - zebrafish (GRCz10 up-to-date, Zv9 from Mar 2015 backward)
        # - Triticum aestivum (IWGSC1+popseq/TGACv1, archive plant)
        # - Zea mays (AGPv3, archive plant)

        # The dictionary below contains the following information:
        # species_assemblies_divisions = {
        #       species_scientific_name: {
        #           assembly_name: division
        #       }
        # }
        species_assemblies_divisions = {
            # if it's human assembly
            # only GRCh38.* and GRCh37.* assemblies are supported,
            # domain is different in the two cases
            # other human assemblies are not supported
            "homo_sapiens": {
                'grch38': 'www',
                'grch37': 'grch37'
            },
            # if it's mouse assembly
            # any GRCm38 patch is supported, other assemblies are not
            "mus_musculus": {
                'grcm38': 'www'
            },
            # if it's rat assembly must take archive into account
            "rattus_norvegicus": {
                'rnor_6': 'www',
                'rnor_5': 'mar2015.archive'
            },
            # if it's zebrafish assembly must take archive into account
            "danio_rerio": {
                'grcz10': 'www',
                'zv9': 'mar2015.archive'
            },
            # if it's fruitfly assembly must take archive into account
            "drosophila_melanogaster": {
                'release_6': 'www',
                'release_5': 'dec2014.archive'
            },
            # Handle old maize assembly
            "zea mays": {
                'b73_refgen_v3': 'archive.plants',
                # AGPv4 is new assembly but doesn't have accession
                'agpv4': 'plants'
            },
            # Handle old wheat assembly, but also new since EG interface doesn't work here
            "triticum_aestivum": {
                'iwgsc1+popseq': 'archive.plants',
                # TGACv1 is the 'newest' old assembly
                'tgac': 'oct2017-plants',
                # IWGSC is new assembly and has accession, but
                # as said above EG interface cannot fetch entry from genome shared db
                # this is weird as same code elsewhere using EG interface works
                'iwgsc': 'plants'
            },
        }

        try:
            division = species_assemblies_divisions.get(species_scientific_name.lower()).get(assembly_name.lower())
        except AttributeError:
            division = None

        if division is None:
            # Normal cases are here
            # see Translator.pm line 1231 onward

            # Look up division using Ensembl Rest API by using providing the assembly accession
            assembly_info_url = 'https://rest.ensembl.org/info/genomes/assembly/' + assembly_accession + ''
            assembly_info_response = requests.get(assembly_info_url, headers={'Accept': 'application/json'}, verify=True)

            # genome_division can be: 'EnsemblVertebrates', 'EnsemblProtists', 'EnsemblMetazoa',
            # 'EnsemblPlants', 'EnsemblFungi' or 'EnsemblBacteria'
            # See: https://rest.ensembl.org/documentation/info/info_divisions
            try:
                genome_division = assembly_info_response.json().get('division')
            except json.decoder.JSONDecodeError:
                genome_division = None

            if genome_division is None:
                # another way to get division is using species_scientific_name with /info/genomes API
                # TODO: Ask if you we can get rid of division look up using assembly above
                #  is fetching using info/genomes sufficient?
                genomes_info_url = 'https://rest.ensembl.org/info/genomes/' + species_scientific_name + ''
                genomes_info_response = requests.get(genomes_info_url, headers={'Accept': 'application/json'}, verify=True)
                try:
                    genome_division = genomes_info_response.json().get('division')
                except json.decoder.JSONDecodeError:
                    genome_division = None

            if genome_division is None:
                # if genome_division is still None get it using taxonomy endpoint, e.g:
                # https://rest.ensembl.org/info/genomes/taxonomy/physcomitrella_patens?content-type=application/json
                genomes_info_url = 'https://rest.ensembl.org/info/genomes/taxonomy/' + species_scientific_name
                genomes_info_response = requests.get(genomes_info_url, headers={'Accept': 'application/json'}, verify=True)
                try:
                    genome_division = genomes_info_response.json()[0].get('division')
                except json.decoder.JSONDecodeError:
                    genome_division = None

            if genome_division is not None:
                genome_division = genome_division.lower()
                if genome_division == 'ensemblvertebrates':
                    division = 'www'
                elif genome_division.startswith('ensembl'):
                    # remove 'ensembl' string
                    division = genome_division[len('ensembl'):]
                else:
                    raise Exception("Genome division: '{}' isn't recognized".format(genome_division))

        # EnsEMBL browser link
        domain = f'http://{division}.ensembl.org'

        if division is None:
            logger.warning("[WARNING] Couldn't fetch division for trackdb ID: {}!".format(self.trackdb_id))
        # if division contains the string 'archive' but not followed by '.plants'
        elif re.search("archive(?!\.plants)", division):
            # link to plant archive site should be the current one
            browser_links['ensembl'] = "{}/{}/Location/View?contigviewbottom=url:{};name={};format=TRACKHUB;#modal_user_data".format(
                domain, species_scientific_name, hub_url, short_label_stripped)
        else:
            browser_links['ensembl'] = "{}/TrackHub?url={};species={};name={};registry=1".format(domain, hub_url,
                                                                                                species_scientific_name,
                                                                                                short_label_stripped)

        # VectorBase browser links
        vectorbase_domain = "https://www.vectorbase.org"

        assembly_accession_species_scientific_name = {
            # handle special case: Anopheles stephensi strain Indian (Anopheles_stephensiI in VB)
            # cannot use species scientific name as it does not have strain
            'GCA_000300775.2': 'Anopheles_stephensi_indian',
            # and similarly for other species, even if it's not planned to have track hubs for them at the moment
            'GCA_000150785.1': 'Anopheles_gambiae_pimperena',
            'GCA_000441895.2': 'Anopheles_sinensis_china',
            # handle another special case: ENA uses Anopheles gambiae M as main species name instead of Anopheles coluzzii
            'GCA_000150765.1': 'Anopheles_coluzzii',
            # updates on Aeges aegypti assemblies
            'GCA_000004015.1': 'Aedes_aegypti_lvp',  # was Aedes_aegypti
            'GCA_002204515.1': 'Aedes_aegypti_lvpagwg',
        }

        species_scientific_name = assembly_accession_species_scientific_name.get(assembly_accession)

        browser_links['vectorbase'] = "{}/TrackHub?url={};species={};name={};registry=1".format(vectorbase_domain,
                                                                                                hub_url,
                                                                                                species_scientific_name,
                                                                                                short_label_stripped)
        return browser_links

    def update_trackdb_document(self, hub, trackdb_data, trackdb_configuration, tracks_status, index):
        # pylint: disable=too-many-arguments
        """
        Update trackdb document in Elascticsearch with the additional data provided
        :param trackdb: trackdb object to be updated
        :param file_type: file type associated with this track
        :param trackdb_data: data array that will be added to the trackdb document
        :param trackdb_configuration: configuration object that will be added to the trackdb document
        :param tracks_status: status dictionary that will be added to the trackdb document
        :param index: index name (default: 'trackhubs')
        """
        try:
            # Connect to ES and prevent Read timed out error
            # https://stackoverflow.com/a/35302158/4488332
            es_conn = connections.Elasticsearch(
                [ELASTICSEARCH_DSL['default']['hosts']],
                verify_certs=True,
                timeout=600,
                max_retries=10,
                retry_on_timeout=True
            )
            es_conn.update(
                index=index,
                id=self.trackdb_id,
                # refresh=True,
                body={
                    'doc': {
                        'owner': hub.get_owner(),
                        'file_type': self.get_trackdb_file_type_count(),
                        'data': trackdb_data,
                        'browser_links': self.generate_browser_links(),
                        'updated': int(time.time()),
                        'source': {
                            'url': self.source_url,
                            # Compute checksum
                            'checksum': hashlib.md5(self.source_url.encode('utf-8')).hexdigest()
                        },
                        # Get the data type based on the hub info
                        'type': trackhubs.models.Hub.objects.filter(data_type_id=hub.data_type_id)
                            .values('data_type__name').first()
                            .get('data_type__name'),
                        'configuration': trackdb_configuration,
                        'status': tracks_status
                    }
                }
            )
            logger.info("Trackdb id {} is updated successfully".format(self.trackdb_id))

        except elasticsearch.exceptions.ConnectionError as es_con_err:
            logger.exception("There was an error while trying to connect to Elasticsearch. "
                             "Please make sure ES service is running and configured properly!"
                             " Reason: {}".format(es_con_err))


class Track(models.Model):
    class Meta:
        db_table = "track"

    track_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    shortLabel = models.TextField(blank=True, null=True)
    longLabel = models.TextField(blank=True, null=True)
    big_data_url = models.TextField(blank=True, null=True)
    html = models.CharField(max_length=255, null=True)
    meta = models.CharField(max_length=255, null=True)
    additional_properties = models.JSONField(null=True)
    # TODO: make sure composite_parent is not used
    # Check if it's replaced with super_track, composite_track and is_multiwig_track
    # composite_parent = models.CharField(max_length=2, null=True)
    super_track = models.CharField(max_length=20, null=True)
    composite_track = models.CharField(max_length=20, null=True)
    is_multiwig_track = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
    trackdb = models.ForeignKey(Trackdb, on_delete=models.CASCADE)
    # Set file_type nullable to true in track table because SuperTracks in JSON dump don't have a type field
    file_type = models.ForeignKey(FileType, on_delete=models.CASCADE, null=True)
    visibility = models.ForeignKey(Visibility, on_delete=models.CASCADE)


class GenomeAssemblyDump(models.Model):
    class Meta:
        db_table = "genome_assembly_dump"

    genome_assembly_dump_id = models.AutoField(primary_key=True)
    accession = models.CharField(max_length=20, null=False)
    version = models.IntegerField(null=True)
    accession_with_version = models.CharField(max_length=20, null=False)
    assembly_name = models.CharField(max_length=255, null=False)
    assembly_title = models.CharField(max_length=255, null=True)
    tax_id = models.IntegerField(null=False)
    scientific_name = models.CharField(max_length=255, null=False)
    ucsc_synonym = models.CharField(max_length=255, null=True)
    api_last_updated = models.CharField(max_length=20, null=True)
