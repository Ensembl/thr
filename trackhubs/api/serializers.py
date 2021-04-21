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
from trackhubs import models


class HubSerializer(serializers.ModelSerializer):
    """
    Generic Hub serializer
    """
    class Meta:
        model = models.Hub
        fields = [
            'hub_id',
            'name',
            'short_label',
            'long_label',
            'url',
            'description_url',
            'email'
        ]


class CustomHubListSerializer(serializers.ModelSerializer):
    """
    Custom Hub structure serializer used for GET trackhub API
    """
    trackdbs = serializers.SerializerMethodField()

    def get_trackdbs(self, obj):
        return obj.get_trackdbs_list_from_hub()

    class Meta(HubSerializer.Meta):
        fields = HubSerializer.Meta.fields + ['trackdbs']


class CustomOneHubSerializer(serializers.ModelSerializer):
    """
    Custom Hub structure serializer used for GET trackhub/:id API
    """
    trackdbs = serializers.SerializerMethodField()

    class Meta:
        model = models.Hub
        fields = [
            'name',
            'short_label',
            'long_label',
            'url',
            'trackdbs'
        ]

    def get_trackdbs(self, obj):
        return obj.get_trackdbs_full_list_from_hub()
