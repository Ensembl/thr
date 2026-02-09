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
from rest_framework import status, authentication, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from thr.settings import ELASTICSEARCH_DSL
from trackhubs.serializers import CustomOneHubSerializer, CustomHubListSerializer
from trackhubs.models import Hub
import trackhubs.translator
from drf_spectacular.utils import extend_schema


class TrackHubList(APIView):
    """
    List all hubs submitted by the current user, or create a new hub.
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomHubListSerializer

    @extend_schema(operation_id="trackhub_list")
    def get(self, request):
        """
        Return the list of available track data hubs for a given user.
        Each trackhub is listed with key/value parameters together with
        a list of URIs of the resources which corresponds to the trackDbs
        beloning to the track hub
        """
        hubs = Hub.objects.filter(owner_id=request.user.id)
        serializer = CustomHubListSerializer(hubs, many=True)
        return Response(serializer.data)

    # Before calling post function, Django starts a transaction. If the response is produced without problems,
    # Django commits the transaction. If the view produces an exception, Django rolls back the transaction
    # https://docs.djangoproject.com/en/2.2/topics/db/transactions/
    @transaction.atomic
    def post(self, request):
        # the parser is used here
        data = request.data
        if 'url' in data:
            hub_url = data['url']
            assemblies = data.get('assemblies')
            data_type = data.get('type')
            current_user = request.user
            run_hubcheck = data.get('run_hubcheck', True)

            # Verification steps
            # Before we submit the hub we make sure that the hub doesn't exist already
            hub_obj = trackhubs.translator.is_hub_exists(hub_url)
            if hub_obj:
                original_owner_id = hub_obj.owner_id
                if original_owner_id == current_user.id:
                    return Response(
                        {'error': f"This hub is already submitted, please use PUT /api/trackhubs/<hub_id> "
                                              f"endpoint to update it, the hub ID is '{hub_obj.hub_id}'"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                return Response(
                    {"error": "This hub is already submitted by a different user!"},
                    status=status.HTTP_403_FORBIDDEN
                )

            result = trackhubs.translator.save_and_update_document(hub_url, data_type, current_user, run_hubcheck)
            if not result:
                return Response(
                    {'error': 'Something went wrong with the hub submission, please make sure that url is correct and working'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if 'error' in result:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(
            {"error": "Something went wrong with the hub submission, please make sure that 'url' field exists"},
            status=status.HTTP_400_BAD_REQUEST
        )


class TrackHubDetail(APIView):
    """
    Retrieve, update or delete a hub instance.
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomOneHubSerializer

    @staticmethod
    def get_hub(primary_key):
        try:
            return Hub.objects.get(pk=primary_key)
        except Hub.DoesNotExist as hub_not_found:
            raise Http404 from hub_not_found

    @extend_schema(operation_id="trackhub_retrieve")
    def get(self, request, pk):
        # pylint: disable=invalid-name
        hub = self.get_hub(pk)
        serializer = CustomOneHubSerializer(hub)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        This function used to update a hub
        """
        hub = self.get_hub(pk)
        # if hub exist
        if hub:
            # check if the current user is the actual owner
            current_user = request.user
            original_owner_id = trackhubs.models.Hub.objects.filter(url=hub.url).first().owner_id
            # True => proceed
            if original_owner_id == current_user.id:
                data = request.data
                if 'url' in data:
                    hub_url = data['url']
                    assemblies = data.get('assemblies')
                    data_type = data.get('type')
                    run_hubcheck = data.get('run_hubcheck', True)

                    result = trackhubs.translator.save_and_update_document(hub_url, data_type, current_user, run_hubcheck)
                    if not result:
                        return Response(
                            {
                                'error': 'Something went wrong with the hub submission, please make sure that url is correct and working'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    if 'error' in result:
                        return Response(result, status=status.HTTP_400_BAD_REQUEST)
                    return Response(result, status=status.HTTP_201_CREATED)

                return Response(
                    {"error": "Something went wrong with the hub submission, please make sure that 'url' field exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # False
            return Response(
                {"error": "The hub you're trying to update is submitted by a different user!"},
                status=status.HTTP_403_FORBIDDEN
            )
        else:
            return Response({"error": "Hub doesn't exist"}, status=status.HTTP_401_UNAUTHORIZED)

    @transaction.atomic
    def delete(self, request, pk):
        # pylint: disable=invalid-name
        hub = self.get_hub(pk)
        trackdbs_ids_list = hub.get_trackdbs_ids_from_hub()

        # delete the trackdb document from Elasticsearch
        # but make sure that only the trackhub owner can delete it
        current_user_id = request.user.id
        hub_original_owner_id = hub.owner_id
        if current_user_id == hub_original_owner_id:
            try:
                es = connections.Elasticsearch(
                    [ELASTICSEARCH_DSL['default']['hosts']],
                    verify_certs=True
                )
                for trackdb_id in trackdbs_ids_list:
                    es.delete(index='trackhubs', id=trackdb_id)
            except elasticsearch.exceptions.NotFoundError:
                return Response(
                    {"error": "The hub doesn't exist, please check using 'GET api/trackhub/{}' endpoint".format(pk)},
                    status.HTTP_404_NOT_FOUND
                )
            except elasticsearch.exceptions.ConnectionError:
                return Response(
                    {"error": "Cannot connect to Elasticsearch"},
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except Exception as exp:
                # pylint: disable = broad-except
                return Response({"error": "An internal error has occurred!"}, status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(
                {
                    "error": "You are not the owner of the hub you're willing to delete, "
                             "please make sure that you entered the correct hub ID. "
                             "You can use 'GET /api/trackhub' to list your hubs"
                },
                status.HTTP_403_FORBIDDEN
            )

        # delete the hub from MySQL
        hub.delete()

        return Response({"success": "Hub '{}' is deleted successfully".format(hub.name)}, status=status.HTTP_200_OK)
