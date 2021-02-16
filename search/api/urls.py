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

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from .views import TrackhubDocumentView

# from search.api import views

# urlpatterns = [
#     path('', views.TrackhubDocumentView.as_view({'post': 'list'})),
# ]

router = DefaultRouter()
books = router.register(r'',
                        TrackhubDocumentView,
                        basename='trackdb_document')

urlpatterns = [
    url(r'^', include(router.urls)),
]
