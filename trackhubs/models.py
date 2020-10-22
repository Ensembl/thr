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
import time

from django.db import models
from django_mysql.models import JSONField


class Species(models.Model):

    class Meta:
        db_table = "species"

    taxon_id = models.IntegerField()
    scientific_name = models.CharField(max_length=255, null=True)
    common_name = models.CharField(max_length=255, null=True)


class DataType(models.Model):

    class Meta:
        db_table = "data_type"

    data_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, default="genomics")


class FileType(models.Model):

    class Meta:
        db_table = "file_type"

    file_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    settings = JSONField()


class Visibility(models.Model):

    class Meta:
        db_table = "visibility"

    visibility_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)


class Hub(models.Model):

    class Meta:
        db_table = "hub"

    hub_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    short_label = models.CharField(max_length=255, null=True)
    long_label = models.CharField(max_length=255, null=True)
    url = models.CharField(max_length=255)
    description_url = models.URLField(null=True)
    email = models.EmailField(null=True)
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    data_type = models.ForeignKey(DataType, on_delete=models.CASCADE)


class Genome(models.Model):

    class Meta:
        db_table = "genome"

    genome_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    trackdb_location = models.CharField(max_length=255)
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE)


class Assembly(models.Model):

    class Meta:
        db_table = "assembly"

    assembly_id = models.AutoField(primary_key=True)
    accession = models.CharField(max_length=255)
    name = models.CharField(max_length=255, null=True)
    long_name = models.CharField(max_length=255, null=True)
    synonyms = models.CharField(max_length=255, null=True)
    genome = models.ForeignKey(Genome, on_delete=models.CASCADE)


class Trackdb(models.Model):

    class Meta:
        db_table = "trackdb"

    trackdb_id = models.AutoField(primary_key=True)
    public = models.BooleanField(default=False)
    # choices is an iterable containing (actual value, human readable name) tuples
    # type = models.CharField(choices=[
    #     ("genomics", "genomics"),
    #     ("epigenomics", "epigenomics"),
    #     ("transcriptomics", "transcriptomics"),
    #     ("proteomics", "proteomics")
    # ], default="genomics", max_length=50)
    # hub = JSONField()  # default=default_hub
    description = models.TextField(null=True)
    version = models.CharField(default="v1.0", max_length=10)
    created = models.IntegerField(default=int(time.time()))
    updated = models.IntegerField(null=True)
    configurations = JSONField()
    status_message = models.CharField(max_length=45, null=True)
    status_last_update = models.CharField(max_length=45, null=True)
    source_url = models.CharField(max_length=255, null=True)
    source_checksum = models.CharField(max_length=255, null=True)
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE)
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE)
    genome = models.ForeignKey(Genome, on_delete=models.CASCADE)

    '''
    fields = [
            'id',
            'public',
            'type',
            #'hub',
            'description',
            'version',
            #'source',
            #'species',
            #'assembly',
            #'data',
            #'assembly',
            #'data',
            #'configuration',
        ]
    '''


class Track(models.Model):

    class Meta:
        db_table = "track"

    track_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    short_label = models.CharField(max_length=255, null=True)
    long_label = models.CharField(max_length=255, null=True)
    big_data_url = models.CharField(max_length=255, null=True)
    html = models.CharField(max_length=255, null=True)
    meta = models.CharField(max_length=255, null=True)
    additional_properties = JSONField()
    composite_parent = models.CharField(max_length=2, null=True)
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
    trackdb = models.ForeignKey(Trackdb, on_delete=models.CASCADE)
    file_type = models.ForeignKey(FileType, on_delete=models.CASCADE)
    visibility = models.ForeignKey(Visibility, on_delete=models.CASCADE)
