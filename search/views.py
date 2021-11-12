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
from collections import OrderedDict

import elasticsearch
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
    FacetedSearchFilterBackend,
)
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet, PageNumberPagination

from elasticsearch_dsl import (
    RangeFacet,
    TermsFacet
)


# We're overriding some methods since we need to stick with POST /search/
# instead of using GET that is used by default in the django_elasticsearch_dsl_drf library
class CustomCompoundSearchFilterBackend(CompoundSearchFilterBackend):
    """
    This custom class gets the 'query' param from the POST body
    (instead of default GET) and send it back to CompoundSearchFilterBackend
    """
    def get_search_query_params(self, request):
        # show all the results if the query is empty or doesn't exist
        user_query = request.data.get('query')
        if not user_query or user_query == "":
            return []
        return [user_query]


class CustomFilteringFilterBackend(FilteringFilterBackend):
    """
    This custom class gets the 'accession', 'hub', 'species' and 'assembly'
    params from the POST body, construct the customised filter and send it
    back to FilteringFilterBackend
    """
    def get_filter_query_params(self, request, view):
        user_filter = {}
        user_accession_filter = request.data.get('accession')
        user_hub_filter = request.data.get('hub')
        user_species_filter = request.data.get('species')
        user_assembly_filter = request.data.get('assembly')
        user_type_filter = request.data.get('type')

        if user_accession_filter:
            user_filter.update({
                # the '__term' is for filtering using AND
                # https://django-elasticsearch-dsl-drf.readthedocs.io/en/latest/advanced_usage_examples.html#filtering
                'accession__term': {
                    'lookup': None,
                    'values': [user_accession_filter],
                    'field': 'assembly.accession.raw',
                    'type': 'doc'
                }
            })

        if user_hub_filter:
            user_filter.update({
                'hub__term': {
                    'lookup': None,
                    'values': [user_hub_filter],
                    'field': 'hub.name.raw',
                    'type': 'doc'
                }
            })

        if user_species_filter:
            user_filter.update({
                'species__term': {
                    'lookup': None,
                    'values': [user_species_filter],
                    'field': 'species.scientific_name.raw',
                    'type': 'doc'
                }
            })

        if user_assembly_filter:
            user_filter.update({
                'assembly__term': {
                    'lookup': None,
                    'values': [user_assembly_filter],
                    'field': 'assembly.name.raw',
                    'type': 'doc'
                }
            })

        if user_type_filter:
            user_filter.update({
                'type__term': {
                    'lookup': None,
                    'values': [user_type_filter],
                    'field': 'type.raw',
                    'type': 'doc'
                }
            })

        return user_filter


class CustomPageNumberPagination(PageNumberPagination):
    """
    This custom class alters the fields names
    'results' becomes 'items' and
    'count' becomes 'total_entries'
    """

    def get_paginated_response(self, data):
        # we catch the data and rename the fields on the fly before passing the response
        paginated_data = OrderedDict(self.get_paginated_response_context(data))
        paginated_data['total_entries'] = paginated_data.pop('count')
        paginated_data['items'] = paginated_data.pop('results')
        return Response(paginated_data)


class TrackdbDocumentListView(DocumentViewSet):
    """The TrackdbDocument view."""

    pagination_class = CustomPageNumberPagination

    document = TrackdbDocument
    serializer_class = TrackdbDocumentSerializer
    
    lookup_field = 'id'
    filter_backends = [
        CustomFilteringFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        CustomCompoundSearchFilterBackend,
        FacetedSearchFilterBackend,
    ]
    # Define search fields
    search_fields = (
        'hub.short_label', 'hub.long_label', 'hub.name',
        'type', 'species.common_name', 'species.scientific_name',
        'assembly.name', 'assembly.ucsc_synonym', 'assembly.accession'
    )
    # Define filtering fields
    filter_fields = {
        'id': None,
        'accession': 'assembly.accession.raw',
        'hub': 'hub.name.raw'
    }
    # Define ordering fields
    ordering_fields = {
        'id': None,
        'hub': 'hub.name.raw',
    }
    # Order by `_score` first.
    ordering = ('_score', '_id', 'hub.name.raw',)

    faceted_search_fields = {
        # 'hub': 'hub.name.raw',  # By default, TermsFacet is used
        'hub': {
            'field': 'hub.name.raw',
            'facet': TermsFacet,  # But we can define it explicitly
            'enabled': True,
        },
        'species': {
            'field': 'species.scientific_name.raw',
            'facet': TermsFacet,
            'enabled': True,
        },
        'assembly': {
            'field': 'assembly.name.raw',
            'facet': TermsFacet,
            'enabled': True,
        },
        'type': {
            'field': 'type.raw',
            'facet': TermsFacet,
            'enabled': True,
        },
    }


class TrackdbDocumentDetailView(APIView):
    """The TrackhubDocumentDetail view."""

    def get(self, request, pk):
        # pylint: disable=invalid-name
        try:
            trackdb_document = TrackdbDocument.get(id=pk)
        except elasticsearch.exceptions.NotFoundError:
            return Response({"error": "TrackDB document not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TrackdbDocumentSerializer(trackdb_document)
        return Response(serializer.data, status=status.HTTP_200_OK)
