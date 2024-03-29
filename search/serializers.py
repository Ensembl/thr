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

    # TODO: find a way to add the score if needed
    # score = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        """Meta options."""

        # Specify the correspondent document class
        document = search.documents.TrackdbDocument

        fields = [
            'trackdb_id',
            'source',
            'hub',
            'version',
            'owner',
            'status',
            'species',
            'assembly',
            'created',
            'type',
        ]

    def get_status(self, obj):
        """Represent status value."""
        try:
            # Convert elasticsearch_dsl.utils.AttrDict to Dictionary and return it
            return obj.status.to_dict()
        except Exception:
            return None

    def get_source(self, obj):
        """Represent source object."""
        try:
            return obj.source.to_dict()
        except Exception:
            return {}

    def get_owner(self, obj):
        """Represent the owner value."""
        try:
            return obj.owner
        except Exception:
            return ''

    def get_type(self, obj):
        """Represent type value."""
        try:
            return obj.type
        except Exception:
            return ''
