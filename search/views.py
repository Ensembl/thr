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
import elasticsearch
from elasticsearch_dsl import connections, Search
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from search.documents import TrackdbDocument
from search.serializers import TrackdbDocumentSerializer

from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    OrderingFilterBackend,
    CompoundSearchFilterBackend,
    DefaultOrderingFilterBackend,
)
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet


# We're overriding some methods since we need to stick with POST /search/
class CustomCompoundSearchFilterBackend(CompoundSearchFilterBackend):

    def get_search_query_params(self, request):
        # show all the results if the query is empty or doesn't exist
        user_query = request.data.get('query')
        if not user_query or user_query == "":
            return []
        return [user_query]


class CustomFilteringFilterBackend(FilteringFilterBackend):

    def get_filter_query_params(self, request, view):
        user_filter = {}
        user_accession_filter = request.data.get('accession')
        user_hub_filter = request.data.get('hub')
        user_species_filter = request.data.get('species')
        user_assembly_filter = request.data.get('assembly')

        if user_accession_filter:
            user_filter.update({
                # the '__term' is for filtering using AND
                # https://django-elasticsearch-dsl-drf.readthedocs.io/en/latest/advanced_usage_examples.html#filtering
                'accession__term': {
                    'lookup': None,
                    'values': [user_accession_filter],
                    'field': 'assembly.accession',
                    'type': 'doc'
                }
            })

        if user_hub_filter:
            user_filter.update({
                'hub__term': {
                    'lookup': None,
                    'values': [user_hub_filter],
                    'field': 'hub.name',
                    'type': 'doc'
                }
            })

        if user_species_filter:
            user_filter.update({
                'species__term': {
                    'lookup': None,
                    'values': [user_species_filter],
                    'field': 'species.scientific_name',
                    'type': 'doc'
                }
            })

        if user_assembly_filter:
            user_filter.update({
                'assembly__term': {
                    'lookup': None,
                    'values': [user_assembly_filter],
                    'field': 'assembly.name',
                    'type': 'doc'
                }
            })

        # print("user_filter ---> ", user_filter)
        return user_filter


class TrackdbDocumentListView(DocumentViewSet):
    """The TrackdbDocument view."""

    document = TrackdbDocument
    serializer_class = TrackdbDocumentSerializer
    lookup_field = 'id'
    filter_backends = [
        # FilteringFilterBackend,
        CustomFilteringFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        CustomCompoundSearchFilterBackend,
    ]
    # Define search fields
    search_fields = (
        'hub.shortLabel', 'hub.longLabel', 'hub.name',
        'type', 'species.common_name', 'species.scientific_name',
        'assembly.name', 'assembly.ucsc_synonym', 'assembly.accession'
    )
    # Define filtering fields
    filter_fields = {
        'id': None,
        # TODO: Add raw analyzer
        'accession': 'assembly.accession',
        'hub': 'hub.name'
    }
    # Define ordering fields
    ordering_fields = {
        'id': None,
        'hub.name': None,
    }
    # Order by `_score` first.
    ordering = ('_score', '_id', 'hub.name',)


class TrackdbDocumentDetailView(APIView):
    """The TrackhubDocumentDetail view."""

    def get(self, request, pk):
        try:
            trackdb_document = TrackdbDocument.get(id=pk)
        except elasticsearch.exceptions.NotFoundError:
            return Response({"error": "TrackDB document not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TrackdbDocumentSerializer(trackdb_document)
        return Response(serializer.data, status=status.HTTP_200_OK)
