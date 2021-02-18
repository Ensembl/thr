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

from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    OrderingFilterBackend,
    CompoundSearchFilterBackend, DefaultOrderingFilterBackend,
)
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet

from search.documents import TrackdbDocument
from .serializers import TrackdbDocumentSerializer


class TrackhubDocumentView(DocumentViewSet):
    """The TrackhubDocument view."""

    document = TrackdbDocument
    serializer_class = TrackdbDocumentSerializer
    lookup_field = 'trackdb_id'

    filter_backends = [
        # FilteringFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        CompoundSearchFilterBackend,
    ]
    # Define search fields
    search_fields = (
        'public',
        'description',
    )
    # Define filtering fields
    filter_fields = {
        'description': 'description.raw',
        # 'city': 'city.raw',
        # 'state_province': 'state_province.raw',
        # 'country': 'country.raw',
    }

    # Define ordering fields
    ordering_fields = {
        'description': None,
        # 'city': None,
        # 'country': None,
    }
    # Specify default ordering
    ordering = ('_score', '_id')
