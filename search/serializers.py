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

from rest_framework import serializers
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

import search.documents


class TrackdbDocumentSerializer(DocumentSerializer):
    """Serializer for Trackdb document."""

    id = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta(object):
        """Meta options."""

        # Specify the correspondent document class
        document = search.documents.TrackdbDocument

        fields = [
            'score',
            'id',
            'version',
            'type',
            'status',
            'hub',
            'species',
            'assembly',
        ]

    def get_type(self, obj):
        """Represent data type value."""
        try:
            return obj.type
        except Exception:
            return ''

    def get_status(self, obj):
        """Represent status value."""
        try:
            minimal_status_info = {
                "last_update": obj.status.last_update,
                "message": obj.status.message
            }
            return minimal_status_info
        except Exception:
            return None

    def get_score(self, obj):
        if hasattr(obj.meta, 'score'):
            return obj.meta.score
        return None

    def get_id(self, obj):
        if hasattr(obj.meta, 'id'):
            return obj.meta.id
        return None
