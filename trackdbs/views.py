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
from django.db import transaction
from django.http import Http404
from elasticsearch_dsl import connections
from rest_framework import authentication, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from thr.settings import ELASTICSEARCH_DSL
from trackdbs.serializers import TrackdbSerializer
from trackhubs.models import Trackdb


class TrackdbDetail(APIView):
    """
    Retrieve or delete a Trackdb instance.
    """
    authentication_classes = [authentication.TokenAuthentication]
    # In Django REST, permissions are applied to the entire View class,
    # but we can take into account aspects of the request (like the method such as GET or POST)
    # in our authorization decision, that's exactly what IsAuthenticatedOrReadOnly does:
    # It allows the unauthenticated users to GET trackdb but doesn't allow DELETE API calls
    permission_classes = [permissions.IsAuthenticated | permissions.IsAuthenticatedOrReadOnly]

    @staticmethod
    def get_trackdb(pk):
        try:
            return Trackdb.objects.get(pk=pk)
        except Trackdb.DoesNotExist as trackdb_not_found:
            raise Http404 from trackdb_not_found

    def get(self, request, pk):
        # pylint: disable=invalid-name
        trackdb = self.get_trackdb(pk)
        serializer = TrackdbSerializer(trackdb)
        return Response(serializer.data)

    @transaction.atomic
    def delete(self, request, pk):
        # pylint: disable=invalid-name
        trackdb = self.get_trackdb(pk)

        # delete the trackdb document from Elasticsearch
        # but make sure that only the trackhub owner can delete it
        current_user_id = request.user.id
        hub = trackdb.get_hub_from_trackdb()
        hub_original_owner_id = hub.owner_id

        if current_user_id == hub_original_owner_id:
            try:
                es_conn = connections.Elasticsearch(
                    [ELASTICSEARCH_DSL['default']['hosts']],
                    verify_certs=True
                )
                es_conn.delete(index='trackhubs', doc_type='doc', id=trackdb.trackdb_id)
            except elasticsearch.exceptions.NotFoundError:
                return Response(
                    {"error": "The trackdb doesn't exist, please check using 'GET api/trackdb/{}' endpoint".format(pk)},
                    status.HTTP_404_NOT_FOUND
                )
            except elasticsearch.exceptions.ConnectionError:
                return Response(
                    {"error": "Cannot connect to Elasticsearch"},
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except Exception as exp:
                return Response({"error": "An internal error has occurred!"}, status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(
                {
                    "error": "You are not the owner of this trackdb, "
                             "please make sure that you entered the correct trackdb ID."
                },
                status.HTTP_403_FORBIDDEN
            )

        # delete the trackdb from MySQL
        trackdb.delete()

        # one last check to do is verifying if the hub is empty (after deleting the last trackdb)
        count_trackdbs = hub.count_trackdbs_in_hub()
        # if it's the case delete the hub from MySQL
        if count_trackdbs == 0:
            hub.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
