# TrackHub Registry

[![Dependency Compatibility Check](https://github.com/Ensembl/thr/actions/workflows/dep_check.yml/badge.svg)](https://github.com/Ensembl/thr/actions/workflows/dep_check.yml)

TrackHub Registry (THR) is a global centralised collection of publicly accessible [track hubs](http://genome.ucsc.edu/goldenPath/help/hgTrackHubHelp.html#Intro). The goal of the project is to allow third parties to advertise track hubs, and to make it easier for researchers around the world to discover and use track hubs containing different types of genomic research data.

This repository is created to give the project a technology refresh while keeping the same core functionalities.

## Prerequisites

* [Python 3.7+](https://www.python.org/downloads/)
* [venv](https://docs.python.org/3/library/venv.html)
* [Elasticsearch 6.3](https://www.elastic.co/downloads/past-releases/elasticsearch-6-3-0)
* [Docker and Docker-compose](https://www.docker.com/products/docker-desktop) are required if you want to use docker containers

## Local deployment

Clone the project

```shell script
git clone https://github.com/Ensembl/thr.git
cd thr
```

### Using Docker (Backend + Frontend)

You can run the whole application ([Frontend](https://github.com/Ensembl/thr_frontend) + [Backend](https://github.com/Ensembl/thr)) using docker-compose:


Uncomment the last line in `Dockerfile`

```bash
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
```

Then run

```shell script
docker-compose -f docker-compose-local.yml up
```

> If it's executed for the first time it will take some time (~10min) to download the necessary images and setup the environment.

* The app will be accessible at: http://127.0.0.1
* And Elasticsearch at: http://127.0.0.1:9200

To stop the docker use:

```shell script
docker-compose -f docker-compose-local.yml stop
```

> The `docker-compose stop` command will stop your containers, but it won't remove them. 

##### Create Elasticsearch index

Get the container ID (while `docker-compose up` is running)

```shell script
docker container ls
```

You'll get somthing like this:
```shell
$ docker container ls
CONTAINER ID   IMAGE                                                 COMMAND                  CREATED          STATUS         PORTS                                                                                  NAMES
fd8d0eed8c88   thr_nginx                                             "/docker-entrypoint.…"   10 minutes ago   Up 2 minutes   0.0.0.0:80->80/tcp, :::80->80/tcp                                                      thr_nginx_1
378be0cb1e26   thr_react                                             "docker-entrypoint.s…"   10 minutes ago   Up 2 minutes   3000/tcp                                                                               thr_react_1
c41390a512be   thr_django                                            "/usr/src/app/entryp…"   10 minutes ago   Up 2 minutes   0.0.0.0:8000->8000/tcp, :::8000->8000/tcp                                              thr_django_1
8b1bc7c4aa46   mysql:5.7                                             "docker-entrypoint.s…"   10 minutes ago   Up 2 minutes   33060/tcp, 0.0.0.0:3306->3306/tcp, :::3306->3306/tcp                                   thr_mysql_1
87b1ca81fa08   docker.elastic.co/elasticsearch/elasticsearch:6.3.0   "/usr/local/bin/dock…"   5 days ago       Up 2 minutes   0.0.0.0:9200->9200/tcp, :::9200->9200/tcp, 0.0.0.0:9300->9300/tcp, :::9300->9300/tcp   elasticsearch
```

Then run the command

```shell script
docker exec -it <thr_django_container_id> python manage.py search_index --rebuild -f
```

`--rebuild` will delete the index if it exists.

> You can restart a specific container by typing: `docker-compose restart elasticsearch` where `elasticsearch` is the container name

##### Importing genome assembly dump

If it's your first time importing genome assembly information/dump from `ENA` use
```shell script
docker exec -it <thr_django_container_id> python manage.py import_assemblies --fetch ena
```

It will fetch assembly info from ENA and dump it in a JSON file (then you can use the command below to populate the database)

An example of how the output will look like:
```shell
docker exec -it 9fe9ad66132a python manage.py import_assemblies --fetch ena 
[ENA] Fetching assemblies from ENA, it may take few minutes...
[ENA] 1075977 Objects are fetched successfully (took 525.88 seconds)
```

If the JSON is already there, you can simply run 
```shell script
docker exec -it 9fe9ad66132a python manage.py import_assemblies
```
that will use the JSON file (located in `./assemblies_dump` directory) and loads it to MySQL table

An example of how the output will look like:
```shell
docker exec -it 9fe9ad66132a python manage.py import_assemblies 
All rows are deleted! Please wait, the import process will take a while
[ENA] 1075977 objects imported successfully to MySQL DB (took 1539.78 seconds)!
```

> The script deletes all the previously imported assemblies are re-populate the new JSON file content.
> 
> This doesn't delete the hubs, nor the info related to them, the assemblies info imported from JSON are stored in a 
> separate table which is used to populate hub-related tables when submitting a new hub

##### Create super user (Optional)

```shell script
docker exec -it <thr_django_container_id> python manage.py createsuperuser
```

##### Additional Docker commands

To removes stopped service containers and anonymous volumes attached use:

```shell script
docker-compose rm -v
```

If we need to rebuild the images again we can use the command:

```shell script
docker-compose up --build
```

The docker-compose down command will stop the containers, but it also removes the stopped containers 
as well as any networks that were created. We can take down 1 step further and add the -v flag to remove all volumes too:

```shell script
docker-compose down -v
```

To take look of what's inside a specific container:

```shell
docker exec -it <container_id> sh
```

### Without Docker (Backend only)

##### Preparing the environment

Create, activate the virtual environment and install the required packages

```shell script
python -m venv thr_env
source thr_env/bin/activate
pip install -r requirements.txt
```

Export the DB Configuration and turn on Debugging if necessary

```shell script
# MySQL
export DB_DATABASE=thr_db  # The DB should already be created
export DB_USER=user
export DB_PASSWORD=password
export DB_HOST=localhost
export DB_PORT=3306
# Elasticsearch
export ES_HOST=localhost:9200
```

Download and run Elasticsearch (follow the installation steps on [Elasticsearch website](https://www.elastic.co/downloads/elasticsearch))

Make migrations, migrate and rebuild ES index

```shell script
python manage.py makemigrations
python manage.py migrate
python manage.py search_index --rebuild -f
```

The last command will create an index called `trackhubs`, we can get the list of indices using the command

```shell script
curl -XGET "http://localhost:9200/_cat/indices"
```

##### Importing genome assembly dump

If it's your first time importing genome assembly information/dump from `ENA` use
```shell script
python manage.py import_assemblies --fetch ena
```

It will fetch assembly info from ENA and dump it in a JSON file then use it to populate the database

If the JSON is already there, you can simply run 
```shell script
python manage.py import_assemblies
```
that will use the JSON file (located in `./assemblies_dump` directory) and loads it to MySQL table

##### Running the application

```shell script
python manage.py runserver
```

The app will be accessible at: http://127.0.0.1:8000

##### Creating superuser (Optional)

```shell script
python manage.py createsuperuser
```


##### Rebuilding and enriching Elasticsearch index (if required)

In case we want to rebuild the ES index with data existing in MySQL, you need to run the following command:

1. Rebuild ES index
```shell script
python manage.py search_index --rebuild 
```

2. Enrich ES docs
```shell script
python manage.py enrich all
```

This will rebuild the ES index and extract `configuration`, `data`, `file type` and `status` objects from MySQL DB and store it back in Elasticsearch by updating the documents.

> You can enrich one specific trackdb (e.g. `python manage.py enrich 1`) or exclude a trackdb (e.g. `python manage.py enrich all --exclude 1`). See `python manage.py enrich -h` for more details

##### Setting up Cron job

The command below will set up a cron job to update trackdb status every Sunday at 00:00

```shell script
python manage.py crontab add 
```

Make sure to run this command every time CRONJOBS is changed in any way. 

> Cron jobs are defined in `thr/settings/base.py`

To get all the active CRONJOBS, run the following command 
```shell script
python manage.py crontab show
```

To remove all the defined CRONJOBS from crontab, run the following command
```shell script
python manage.py crontab remove
```

> You need to restart the server for changes to take effect 

## APIs Endpoints

See [APIs Endpoints status](apis_endpoints_status.md)