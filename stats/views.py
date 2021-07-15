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
from django.db.models import Count

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from trackhubs.models import Species, Assembly, Trackdb, Track, Hub


class SummaryStatsView(APIView):
    def get(self, request):
        """
        GET method for /api/stats/summary
        Generates a JSON list of properties to render in graph form.
        e.g.
        [
          [ 'Element', ', { 'role': 'style' } ],
          [ 'Hubs', 7274, 'color: gray' ],
          [ 'Species', 140, 'color: #76A7FA' ],
          [ 'Assemblies', 161, 'opacity: 0.2' ]
        ]
        The structure may change in the future depending on what React FE requires to render the graph
        """
        try:
            summary = [
                ['Element', '', {'role': 'style'}],
                # Hubs summary
                ['Hubs', Hub.objects.count(), 'color: gray'],
                # Species summary
                ['Species', Species.objects.count(), 'color: #76A7FA'],
                # Assemblies summary
                ['Assemblies', Assembly.objects.count(), 'opacity: 0.2']
            ]

            return Response(summary, status=status.HTTP_200_OK)

        except django.db.OperationalError:
            return Response(
                {'message': 'Error: Failed to connect to the database'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CompleteStatsView(APIView):
    def get(self, request):
        """
        Action for /api/stats/complete. Returns complete data with which to build
        various stats based on species/assembly/file type on a dedicated page.
        This endpoint is NOT documented publicly for some reason
        """
        complete_stats = {
            'hubs_per_species': {
                # 'comment': 'The number in front of each species is the hubs count'
            },
            'hubs_per_assemblies': {
                # 'comment': 'The number in front of each assembly is the hubs count'
            },
            'hubs_per_file_type': {
                # 'comment': 'The number in front of each file type is the hubs count'
            },
            'species_per_file_type': {
                # 'comment': 'The number in front of each file type is the species count'
            },
            'assemblies_per_file_type': {
                # 'comment': 'The number in front of each file type is the assemblies count'
            },
            'tracks_per_file_type': {
                # 'comment': 'The number in front of each file type is the tracks count'
            },
        }

        # IDEA: Can we DRY the section below or it will make the code harder to understand?

        try:
            # hubs_per_species stats
            hubs_per_species_query = Trackdb.objects.values('species__scientific_name').annotate(total=Count('hub_id'))
            for hubs_per_species_stats in hubs_per_species_query:
                complete_stats['hubs_per_species'].update({
                    hubs_per_species_stats['species__scientific_name']: hubs_per_species_stats['total']
                })

            # hubs_per_assemblies stats
            hubs_per_assemblies_query = Trackdb.objects.values('assembly__name').annotate(total=Count('hub_id'))
            for hubs_per_assemblies_stats in hubs_per_assemblies_query:
                complete_stats['hubs_per_assemblies'].update({
                    hubs_per_assemblies_stats['assembly__name']: hubs_per_assemblies_stats['total']
                })

            # hubs_per_file_type stats
            # How it works:
            #   Track(has file_type id) --> Trackdb(has hub id)
            #   we get the file_type__name value and count (with distinct) based on the hub id
            #   select_related is just for optimisation
            hubs_per_file_type_query = Track.objects.select_related('trackdb').values('file_type__name').annotate(total=Count('trackdb__hub__hub_id', distinct=True))
            # print('hubs_per_file_type_query --> ', hubs_per_file_type_query)
            for hubs_per_file_type_stats in hubs_per_file_type_query:
                complete_stats['hubs_per_file_type'].update({
                    hubs_per_file_type_stats['file_type__name']: hubs_per_file_type_stats['total']
                })

            # species_per_file_type stats
            # How it works:
            #   Track(has file_type id) --> Trackdb(has species id)
            #   we get the file_type__name value and count (with distinct) based on the species id
            #   select_related is just for optimisation
            species_per_file_type_query = Track.objects.select_related('trackdb').values('file_type__name').annotate(total=Count('trackdb__species__id', distinct=True))
            for species_per_file_type_stats in species_per_file_type_query:
                complete_stats['species_per_file_type'].update({
                    species_per_file_type_stats['file_type__name']: species_per_file_type_stats['total']
                })

            # assemblies_per_file_type stats
            # How it works:
            #   Track(has file_type id) --> Trackdb(has assembly id)
            #   we get the file_type__name value and count (with distinct) based on the assembly id
            #   select_related is just for optimisation
            assemblies_per_file_type_query = Track.objects.select_related('trackdb').values('file_type__name').annotate(total=Count('trackdb__assembly__assembly_id', distinct=True))
            for assemblies_per_file_type_stats in assemblies_per_file_type_query:
                complete_stats['assemblies_per_file_type'].update({
                    assemblies_per_file_type_stats['file_type__name']: assemblies_per_file_type_stats['total']
                })

            # tracks_per_file_type stats
            tracks_per_file_type_query = Track.objects.values('file_type__name').annotate(total=Count('file_type_id'))
            for tracks_per_file_type_stats in tracks_per_file_type_query:
                complete_stats['tracks_per_file_type'].update({
                    tracks_per_file_type_stats['file_type__name']: tracks_per_file_type_stats['total']
                })

            return Response(complete_stats, status=status.HTTP_200_OK)

        except django.db.OperationalError:
            return Response(
                {'message': 'Error: Failed to connect to the database'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
