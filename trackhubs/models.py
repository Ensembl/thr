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

from django.db import models
from django_mysql.models import JSONField


class Trackdb(models.Model):

    public = models.BooleanField(default=False)
    # choices is an iterable containing (actual value, human readable name) tuples
    type = models.CharField(choices=[
        ("genomics", "genomics"),
        ("epigenomics", "epigenomics"),
        ("transcriptomics", "transcriptomics"),
        ("proteomics", "proteomics")
    ], default="genomics", max_length=50)
    hub = JSONField()  # default=default_hub
    description = models.TextField(null=True)
    version = models.CharField(default="v1.0", max_length=10)

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
