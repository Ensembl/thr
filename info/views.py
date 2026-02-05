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
import django
import elasticsearch
from rest_framework.pagination import LimitOffsetPagination

from rest_framework.views import APIView
from rest_framework.response import Response

from info.serializers import AssemblyInfoSerializer, TrackhubInfoSerializer
from thr.settings import ELASTICSEARCH_DSL
from rest_framework import status
from django.conf import settings

from trackhubs.models import Species, Assembly, Trackdb, Track, Hub


class VersionInfoView(APIView):

    def get(self, request):
        """
        GET method for /api/info/version
        Returns the current version of all the Registry APIs.
        If the request is successful, the Response is an hash with one key, version,
        whose value is a string which identifies the API version.
        """
        return Response({'version': settings.THR_VERSION})


class PingInfoView(APIView):
    def get(self, request):
        """
        GET method for /api/info/ping
        Checks if the service is alive.
        If the request is successful, the response is a hash with one key, ping.
        If it's value is 1 the service is available.
        """
        es_instance = elasticsearch.Elasticsearch(
            [ELASTICSEARCH_DSL['default']['hosts']],
            verify_certs=True
        )

        if es_instance.ping():
            return Response({'ping': 1}, status=status.HTTP_200_OK)
        return Response({'message': 'Error: Service Unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class SpeciesInfoView(APIView):
    def get(self, request):
        """
        GET method for /api/info/species
        Returns the set of species the track hubs registered in the Registry contain data for.
        If the request is successful, the response is an array containing the scientific names of the species.
        """
        try:
            species_list = Species.objects.values_list('scientific_name', flat=True)
            return Response(species_list, status=status.HTTP_200_OK)
        except django.db.OperationalError:
            return Response(
                {'message': 'Error: Failed to connect to the database'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AssembliesInfoView(APIView):
    def get(self, request):
        """
        GET method for /api/info/assemblies
        Returns the set of assemblies the track hubs registered in the Registry contain data for.
        The returned assemblies are grouped by their corresponding species.
        If the request is successful, the response is a hash where a key is a species scientific name,
        and whose value is an array of hashes, each one representing an assembly for that species and containing
        its name, synonyms and accession.
        {'species.scientific_name' : [{'synonyms': ['synonyms.value'], 'name': 'name.value', 'accession': 'accession.value'}, ..]}
        e.g:
        {'Homo sapiens': [{'synonyms': ['hg19'], 'name': 'GRCh37', 'accession': 'GCA_000001405.1'},
                          {'synonyms': ['hg38'], 'name': 'GRCh38', 'accession': 'GCA_000001405.15'}]}
        """
        assemblies_set = {}
        try:
            # TODO: decide either to keep the id as the primary key or use just taxon_id instead
            species_ids_list = Species.objects.values_list('id', 'scientific_name')
            # based on the ER diagram, in order to get species and assemblies info we need to cross the trackdb table
            # species -> trackdb -> assembly
            for species_id, sci_name in species_ids_list:
                assemblies_set[sci_name] = []
                # get the assembly_ids that are linked to trackdbs associated to this species_id and remove redundant ones
                assembly_ids = set(Trackdb.objects.filter(species_id=species_id).values_list('assembly_id', flat=True))

                # We sort IDs to keep response ordering stable for tests.
                for assembly_id in sorted(assembly_ids):
                    assembly = Assembly.objects.get(assembly_id=assembly_id)
                    serializer = AssemblyInfoSerializer(assembly)
                    assemblies_set[sci_name].append(serializer.data)

            return Response(assemblies_set, status=status.HTTP_200_OK)

        except django.db.OperationalError:
            return Response(
                {'message': 'Error: Failed to connect to the database'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HubPerAssemblyInfoView(APIView):
    def get(self, request, assembly):
        """
        GET method for /api/info/hubs_per_assembly/:assembly
        Returns the number of hubs for a given assembly, specified either by INSDC name or accession.
        If the request is successful, the response is a hash with a key "tot", whose value is
        the total number of hubs which contains data for the specified assembly.
        """
        try:
            # term_field = 'accession' if assembly.startswith('GCA') else 'name'
            if assembly.startswith('GCA'):
                assembly_id = Assembly.objects.filter(accession=assembly).values_list('assembly_id', flat=True).first()
            else:
                assembly_id = Assembly.objects.filter(name=assembly).values_list('assembly_id', flat=True).first()

            hub_count = Trackdb.objects.filter(assembly_id=assembly_id).count()
            return Response({'tot': hub_count}, status=status.HTTP_200_OK)
        except django.db.OperationalError:
            return Response(
                {'message': 'Error: Failed to connect to the database'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TracksPerAssemblyInfoView(APIView):
    def get(self, request, assembly):
        """
        GET method for /api/info/tracks_per_assembly/:assembly
        Returns the number of tracks for a given assembly, specified by INSDC name or accession.
        If the request is successful, the response is a hash with a key "tot", whose value is the
        total number of tracks which contains data for the specified assembly.
        """
        try:
            if assembly.startswith('GCA'):
                assembly_id = Assembly.objects.filter(accession=assembly).values_list('assembly_id', flat=True).first()
            else:
                assembly_id = Assembly.objects.filter(name=assembly).values_list('assembly_id', flat=True).first()

            trackdb_ids = Trackdb.objects.filter(assembly_id=assembly_id).values_list('trackdb_id', flat=True)

            # TODO: check if this can be done in one shot using in_bulk
            track_count = 0
            for trackdb_id in trackdb_ids:
                # count how many tracks belong to this specific assembly
                this_track_count = Track.objects.filter(trackdb_id=trackdb_id).count()
                track_count += this_track_count

            return Response({'tot': track_count}, status=status.HTTP_200_OK)

        except django.db.OperationalError:
            return Response(
                {'message': 'Error: Failed to connect to the database'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TrackhubsInfoView(APIView, LimitOffsetPagination):
    def get(self, request):
        """
        GET method for /api/info/trackhubs
        Return the list of registered track data hubs.
        If the request is successful, the response is an array of hashes identifying trackhubs.
        Each trackhub hash has the following key/value pairs:
            name: the single-word name of the directory containing the track hub files;
            url: the track hub remote URL;
            shortLabel: the short name for the track hub;
            longLabel: the longer descriptive label for the track hub;
            trackdbs: a list of hashes containing information for each trackDb (i.e. assembly specific data files)
            registered for the track hub. Each trackDb hash contains the species NCBI tax id and assembly accession,
            and the URI of the JSON representation of the trackDb which can be retrieved from the Registry.
        The end result will be something like this:
        {
            "name": "track_hub",
            "shortLabel": "GRC Genome Issues under Review",
            "longLabel": "Genome Reference Consortium: Genome issues and other features",
            "url": "http://ngs.sanger.ac.uk/production/grit/track_hub/hub.txt",
            "trackdbs": [
                {
                  "species": "9606",
                  "uri": "https://www.trackhubregistry.org/api/search/trackdb/27",
                  "assembly": "GCA_000001405.15"
                }, ..
            ]
        }
        """
        try:
            all_trackhubs = Hub.objects.all()
            paginate_result = self.paginate_queryset(all_trackhubs, request, view=self)
            serializer = TrackhubInfoSerializer(paginate_result, many=True)
            return self.get_paginated_response(serializer.data)

        except django.db.OperationalError:
            return Response(
                {'message': 'Error: Failed to connect to the database'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
