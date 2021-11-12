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
from datetime import datetime

from rest_framework import serializers
from trackhubs import models


class TrackdbHubSerializer(serializers.ModelSerializer):
    """
    Short Hub serializer
    """
    class Meta:
        model = models.Hub
        fields = [
            'name',
            'short_label',
            'long_label',
            'url',
        ]


class TrackdbSpeciesSerializer(serializers.ModelSerializer):
    """
    Species serializer
    """
    class Meta:
        model = models.Species
        fields = [
            'scientific_name',
            'common_name',
            'taxon_id',
        ]


class TrackdbAssemblySerializer(serializers.ModelSerializer):
    """
    Assembly serializer
    """
    class Meta:
        model = models.Assembly
        fields = [
            'name',
            'accession',
            'ucsc_synonym',
        ]


class TrackdbSerializer(serializers.ModelSerializer):
    """
    Trackdb serializer, same structure as in:
    https://www.trackhubregistry.org/docs/api/registration/reference#get_trackdb
    """
    owner = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()
    updated = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()
    hub = serializers.SerializerMethodField()
    species = serializers.SerializerMethodField()
    assembly = serializers.SerializerMethodField()

    class Meta:
        model = models.Trackdb
        fields = [
            'owner',
            'file_type',
            'created',
            'updated',
            'version',
            'type',
            'source',
            'hub',
            'species',
            'assembly',
            # 'data',
            'configuration',
            'status'
        ]

    @staticmethod
    def get_owner(obj):
        hub = models.Hub.objects.filter(hub_id=obj.hub.hub_id).first()
        return hub.get_owner()

    @staticmethod
    def get_created(obj):
        return datetime.utcfromtimestamp(obj.created).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_updated(obj):
        return datetime.utcfromtimestamp(obj.updated).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_source(obj):
        return {
            'checksum': obj.source_checksum,
            'url': obj.source_url
        }

    @staticmethod
    def get_type(obj):
        return models.DataType.objects.values_list('name', flat=True).get(data_type_id=obj.hub.data_type_id)

    @staticmethod
    def get_hub(obj):
        hub = models.Hub.objects.filter(hub_id=obj.hub.hub_id).first()
        return TrackdbHubSerializer(hub).data

    @staticmethod
    def get_species(obj):
        species = models.Species.objects.filter(taxon_id=obj.species.taxon_id).first()
        return TrackdbSpeciesSerializer(species).data

    @staticmethod
    def get_assembly(obj):
        assembly = models.Assembly.objects.filter(assembly_id=obj.assembly.assembly_id).first()
        return TrackdbAssemblySerializer(assembly).data

    @staticmethod
    def get_file_type(obj):
        return obj.get_trackdb_file_type_count()
