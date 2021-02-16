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

from rest_framework import serializers
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from search.documents import TrackdbDocument


class TrackdbDocumentSerializer(DocumentSerializer):
    """Serializer for Trackdb document."""

    description = serializers.CharField(read_only=True)

    class Meta(object):
        """Meta options."""

        # Specify the correspondent document class
        document = TrackdbDocument

        # Note, that since we're using a dynamic serializer,
        # we only have to declare fields that we want to be shown. If
        # somehow, dynamic serializer doesn't work for you, either extend
        # or declare your serializer explicitly.
        fields = (
            'trackdb_id',
            'hub',
            'public',
            'description',
            # 'assembly',
            'configuration',
            'data',
            'type',
            'species',
            'version',
            'created',
            'updated',
            # 'status_message',
            # 'status_last_update',
            # 'status',
            # 'source_url',
            # 'source_checksum',
        )

    # def get_location(self, obj):
    #     """Represent location value."""
    #     try:
    #         return obj.location.to_dict()
    #     except:
    #         return {}
