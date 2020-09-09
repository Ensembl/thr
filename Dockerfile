FROM python:3.7-alpine

# Add scripts to the PATH
# This will allow us to access scripts directly in the container
ENV PATH="/scripts:${PATH}"

COPY ./requirements.txt ./requirements.txt

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
RUN pip install -r /requirements.txt
RUN apk del .tmp

RUN mkdir /thr
COPY ./thr /thr
WORKDIR /thr
COPY ./scripts /scripts

RUN chmod +x /scripts/*

# Contains content uploaded by users
RUN mkdir -p /vol/web/media
# Contains JS, CSS etc
RUN mkdir -p /vol/web/static

RUN adduser -D user
RUN chown -R user:user /vol
RUN chmod -R 755 /vol/web

# switch to the user created
USER user

# entrypoint.sh runs uWSGI and start the django app
CMD ["entrypoint.sh"]
