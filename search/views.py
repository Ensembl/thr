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


class TrackdbDocumentListView(APIView):
    """The TrackhubDocumentList view."""

    document = TrackdbDocument
    serializer_class = TrackdbDocumentSerializer
    # lookup_field = 'trackdb_id'

    def post(self, request):
        query = request.data.get('query')
        species = request.data.get('species')
        assembly = request.data.get('assembly')
        hub = request.data.get('hub')
        accession = request.data.get('accession')

        client = connections.Elasticsearch()
        all_queries = Search(using=client)

        if not request.data:
            return Response({"error": "Missing message body in request"}, status=status.HTTP_400_BAD_REQUEST)
            # in case we want to show all the data:
            # all_results = s.execute().to_dict()
            # return Response(all_results, status=status.HTTP_200_OK)
        if not query:
            return Response({"error": "Missing query field"}, status=status.HTTP_400_BAD_REQUEST)

        search_fields = [
            'hub.shortLabel', 'hub.longLabel', 'hub.name',
            'type', 'species.common_name', 'species.scientific_name'
        ]
        all_queries = all_queries.query("multi_match", query=query, fields=search_fields)

        if accession:
            all_queries = all_queries.filter('term', assembly__accession=accession)

        if species:
            all_queries = all_queries.filter('term', species__scientific_name=species)

        if hub:
            all_queries = all_queries.filter('term', hub__name=hub)

        if assembly:
            all_queries = all_queries.filter('term', assembly__name=assembly)

        s_result = all_queries.execute().to_dict()
        return Response(s_result, status=status.HTTP_200_OK)


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
