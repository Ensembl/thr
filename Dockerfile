# See the NOTICE file distributed with this work for additional information
# regarding copyright ownership.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM python:3.10.14

# set work directory
WORKDIR /usr/src/app

# set environment variables to create Python byte cache to speed up Python a little bit (optional)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy our django project
COPY . .
# install dependencies
RUN pip install -r /usr/src/app/requirements.txt

# bake static assets into the image
ENV DJANGO_ENV=production
ENV DEBUG=0
RUN python manage.py collectstatic --noinput --settings=thr.settings.prod

# run entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh
# NOTE: Uncomment the line below when running docker compose
# It's disabled for the sake of Kubernetes deployment
# ENTRYPOINT ["/usr/src/app/entrypoint.sh"]


# Useful resources:
# https://datagraphi.com/blog/post/2020/8/30/docker-guide-build-a-fully-production-ready-machine-learning-app-with-react-django-and-postgresql-on-docker
