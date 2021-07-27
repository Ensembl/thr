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

# Required alpine packages to install uWSGI server in order to run django app
RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers

# install dependencies
COPY ./requirements.txt .
RUN pip install -r /usr/src/app/requirements.txt
RUN apk del .tmp

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# copy our django project
COPY ./thr .

# run entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]


# Useful resources:
# https://datagraphi.com/blog/post/2020/8/30/docker-guide-build-a-fully-production-ready-machine-learning-app-with-react-django-and-postgresql-on-docker
