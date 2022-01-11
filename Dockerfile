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

FROM python:3.7.9-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables to create Python byte cache to speed up Python a little bit (optional)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# required packages to install mysql
# https://github.com/gliderlabs/docker-alpine/issues/181
RUN apk add --no-cache mariadb-connector-c-dev ;\
    apk add --no-cache --virtual .build-deps \
        build-base \
        mariadb-dev ;\
    pip install mysqlclient;\
    apk del .build-deps

# Fix: Error loading shared library libstdc++.so.6: No such file or directory (needed by ./hubCheck)
#      Error loading shared library libgcc_s.so.1: No such file or directory (needed by ./hubCheck)
#      Error relocating /usr/src/app/tools/hubCheck: qsort_r: symbol not found
# and many others (when running hubcheck $ ldd ./hubcheck)
RUN apk update --no-cache && \
    apk upgrade --no-cache && \
    apk add --no-cache curl bash openssl libgcc libstdc++ ncurses-libs libc-dev patch g++ gcompat
# download hubcheck utility
RUN mkdir tools ;\
    curl -o tools/hubCheck http://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64/hubCheck ;\
    chmod u+x tools/hubCheck

# Required alpine packages to install uWSGI server in order to run django app
RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers

# copy our django project
COPY . .
# install dependencies
#COPY ./requirements.txt .
RUN pip install -r /usr/src/app/requirements.txt
RUN apk del .tmp

# copy entrypoint.sh
#COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# run entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh
# NOTE: Uncomment the line below when running docker compose
# It's disabled for the sake of Kubernetes deployment
# ENTRYPOINT ["/usr/src/app/entrypoint.sh"]


# Useful resources:
# https://datagraphi.com/blog/post/2020/8/30/docker-guide-build-a-fully-production-ready-machine-learning-app-with-react-django-and-postgresql-on-docker
