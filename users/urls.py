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

from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from users.views import RegistrationViewAPI, LogoutViewAPI, UserDetailsView, ChangePasswordView

urlpatterns = [
    path('user/', UserDetailsView.as_view(), name='user_api'),
    path('register', RegistrationViewAPI.as_view(), name='register_api'),
    path('login', obtain_auth_token, name='login_api'),
    path('logout', LogoutViewAPI.as_view(), name='logout_api'),
    path('logout', LogoutViewAPI.as_view(), name='logout_api'),
    path('change_password', ChangePasswordView.as_view(), name='change_password_api'),
]
