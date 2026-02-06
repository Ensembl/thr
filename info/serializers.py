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

from thr import settings
from trackhubs import models


class AssemblyInfoSerializer(serializers.ModelSerializer):
    """
    Assembly info serializer
    """
    synonyms = serializers.SerializerMethodField()

    def get_synonyms(self, obj) -> list[str]:
        # this gives us the possibility to add other synonyms in the future
        return [obj.ucsc_synonym]

    class Meta:
        model = models.Assembly
        fields = [
            'name',
            'accession',
            'synonyms',
        ]


class TrackhubInfoSerializer(serializers.ModelSerializer):
    """
    Trackhub info serializer
    """

    trackdbs = serializers.SerializerMethodField()

    class Meta:
        model = models.Hub
        fields = [
            'name',
            'shortLabel',
            'longLabel',
            'url',
            'trackdbs'
        ]

    def get_trackdbs(self, obj) -> list[dict]:
        trackdbs_short_info = []
        trackdbs = obj.get_trackdbs_full_list_from_hub()
        for trackdb in trackdbs:
            trackdbs_short_info.append({
                'species': trackdb.get('species').get('tax_id'),
                'uri': 'http://' + settings.BACKEND_URL + '/api/search/trackdb/' + str(trackdb.get('trackdb_id')),
                'assembly': trackdb.get('assembly').get('accession')
            })
        return trackdbs_short_info


class VersionInfoResponseSerializer(serializers.Serializer):
    version = serializers.CharField()


class PingInfoResponseSerializer(serializers.Serializer):
    ping = serializers.IntegerField()


class SpeciesListResponseSerializer(serializers.Serializer):
    species = serializers.ListField(child=serializers.CharField())


class AssembliesInfoResponseSerializer(serializers.Serializer):
    assemblies = serializers.DictField(child=AssemblyInfoSerializer(many=True))


class CountResponseSerializer(serializers.Serializer):
    tot = serializers.IntegerField()
