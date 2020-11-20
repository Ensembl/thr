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
from django.http import Http404
from elasticsearch_dsl import connections
from rest_framework import status, authentication, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from trackhubs.api.serializers import HubSerializer
from trackhubs.models import Hub
from trackhubs.parser import save_and_update_document


class HubList(APIView):
    """
    List all hubs submitted by the current user, or create a new hubs.
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        hubs = Hub.objects.filter(owner_id=request.user.id)
        serializer = HubSerializer(hubs, many=True)
        return Response(serializer.data)

    def post(self, request):
        # the parser is used here
        data = request.data
        if 'url' in data:
            hub_url = data['url']
            assemblies = data.get('assemblies')
            data_type = data.get('type')
            current_user = request.user
            result = save_and_update_document(hub_url, data_type, current_user)
            if not result:
                return Response(
                    {'error': 'Something went wrong with the hub submission, please make sure that url is correct'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if 'error' in result:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(
            {"error": "Something went wrong with the hub submission, please make sure that 'url' field exists"},
            status=status.HTTP_400_BAD_REQUEST
        )


class HubDetail(APIView):
    """
    Retrieve or delete a trackhub instance.
    TODO: add access permissions
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_hub(self, pk):
        try:
            return Hub.objects.get(pk=pk)
        except Hub.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        hub = self.get_hub(pk)
        serializer = HubSerializer(hub)
        return Response(serializer.data)

    def delete(self, request, pk):
        # TODO: Meke sure that only the trackhub owner can delete it
        hub = self.get_hub(pk)
        trackdbs_ids_list = hub.get_trackdbs_ids()

        try:
            es = connections.Elasticsearch()
        except Exception as e:
            print(e)

        # delete the trackdb document from Elasticsearch
        try:
            for trackdb_id in trackdbs_ids_list:
                es.delete(index='trackhubs', doc_type='doc', id=trackdb_id)
        except elasticsearch.exceptions.NotFoundError:
            return Response(
                {"error": "The hub doesn't exist, please check using 'GET api/trackhub/{}' endpoint".format(pk)},
                status.HTTP_404_NOT_FOUND
            )

        # delete the hub from MySQL
        hub.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
