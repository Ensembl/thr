# TrackHub Registry

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

### Using Docker

Fire up docker-compose, it will take some time to download the necessary images and setup the environment


```shell script
docker-compose up
```

The app will be accessible at: http://127.0.0.1:8000
Elasticsearch: http://127.0.0.1:9200

To stop the docker use:

```shell script
docker-compose stop
```

To removes stopped service containers and anonymous volumes attached use:

```shell script
docker-compose rm -v
```

If we need to rebuild the images again we can use the command:

```shell script
docker-compose up --build
```

##### Create Elasticsearch index

Get the container ID (while `docker-compose up` is running)

```shell script
docker container ls
```

Then run the command

```shell script
docker exec -it <thr_web_container_id> python manage.py search_index --rebuild -f
```

`--rebuild` will delete the index if it exists.

##### Create super user (Optional)

```shell script
docker exec -it <thr_web_container_id> python manage.py createsuperuser
```

### Without Docker

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
export THR_DB_NAME=thr_db  # The DB should already be created
export DEBUG=1
export THR_DB_NAME=thr_db  # The DB should already be created
export THR_DB_USER=user
export THR_DB_PASSWORD=password
export THR_HOST=localhost
export THR_PORT=3306
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

The last command will create an index called `trackhubs` (the index schema is still WIP), we can get the list of indices using the command

```shell script
curl -XGET "http://localhost:9200/_cat/indices"
```

##### Importing genome assembly dump

If it's your first time importing genome assembly information/dump from `ENA` use
```shell script
python manage.py import_assemblies --fetch ena
```

> `UCSC` and `Ensembl` will also be added later.

So that it creates the JSON file, otherwise you can simply run 
```shell script
python manage.py import_assemblies
```
And it will use the already existing JSON file(s) (located in `./assemblies_dump` directory)and loads them to MySQL table

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

In case we want to rebuild the ES index with data existing in MySQL, you need to:

1. Rebuild ES index
```shell script
python manage.py search_index --rebuild -f
```
This will load portion of the data from MySQL to ES

2. Run the `enrich` command that extract `configuration`, `data` and `file type` objects from MySQL DB and store it back in Elasticsearch by updating the documents.

```shell script
python manage.py enrich 
```

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