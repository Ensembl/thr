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
from trackdbs.serializers import TrackdbSerializer
from trackhubs.models import Hub, Trackdb
from rest_framework.response import Response


class TrackdbDetail(APIView):
    """
    Retrieve or delete a Trackdb instance.
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_trackdb(self, pk):
        try:
            return Trackdb.objects.get(pk=pk)
        except Trackdb.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        trackdb = self.get_trackdb(pk)
        serializer = TrackdbSerializer(trackdb)
        return Response(serializer.data)

    @transaction.atomic
    def delete(self, request, pk):
        trackdb = self.get_trackdb(pk)

        # delete the trackdb document from Elasticsearch
        # but make sure that only the trackhub owner can delete it
        current_user_id = request.user.id
        hub_original_owner_id = trackdb.get_hub_owner_id_from_trackdb()

        if current_user_id == hub_original_owner_id:
            try:
                es = connections.Elasticsearch()
                es.delete(index='trackhubs', doc_type='doc', id=trackdb.trackdb_id)
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
            except Exception as e:
                return Response({"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)
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

        return Response(status=status.HTTP_204_NO_CONTENT)
