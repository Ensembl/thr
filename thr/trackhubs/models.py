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

import datetime


class Trackdb(models.Model):

    #class Meta:
        #managed = False

    assembly = models.CharField(max_length=100)
    created = models.DateField(max_length=50, default=datetime.date.today)
    # choices is an iterable containing (actual value, human readable name) tuples
    file_type = models.CharField(choices=[
        ("bam", "bam"),
        ("bed", "bed"),
        ("bigBed", "bigBed")
    ], max_length=100)
