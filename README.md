## TrackHub Registry

TrackHub Registry (THR) is a global centralised collection of publicly accessible [track hubs](http://genome.ucsc.edu/goldenPath/help/hgTrackHubHelp.html#Intro). The goal of the project is to allow third parties to advertise track hubs, and to make it easier for researchers around the world to discover and use track hubs containing different types of genomic research data.

This repository is created to give the project a technology refresh while keeping the same core functionalities.

### Prerequisites

* [Python 3.7+](https://www.python.org/downloads/)
* [venv](https://docs.python.org/3/library/venv.html)
* [Elasticsearch 6.3](https://www.elastic.co/downloads/past-releases/elasticsearch-6-3-0)
* [Docker and Docker-compose](https://www.docker.com/products/docker-desktop) are required if you want to use docker containers

> [Kibana 6.3](https://www.elastic.co/downloads/past-releases/kibana-6-3-0) is not a prerequisite but recommended to explore and execute Elasticsearch queries.

### Local deployment

Clone the project

```shell script
git clone https://github.com/Ensembl/thr.git
cd thr
```

#### Using Docker

Fire up docker-compose, it will take some time to download the necessary images and setup the environment


```shell script
docker-compose up
```

The app will be accessible at: http://127.0.0.1:8000
Elasticsearch: http://127.0.0.1:9200
Kibana: http://127.0.0.1:5601

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

#### Without Docker

Create, activate the virtual environment and install the required packages

```shell script
python -m venv thr_env
source thr_env/bin/activate
pip install -r requirements.txt
```

Export the DB Configuration and turn on Debugging if necessary

```shell script
# MySQL
export THR_DB_NAME=thr_users  # The DB should already be created
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

You can (optional but recommended) download and run Kibana too ([installation steps](https://www.elastic.co/downloads/kibana)).

Migrate and Rebuild ES index

```shell script
python manage.py migrate
python manage.py search_index --rebuild -f
```

The last command will create an index called `trackhubs` (the index schema is still WIP), we can get the list of indices using the command

```shell script
curl -XGET "http://localhost:9200/_cat/indices"
```

To enrich the trackhubs indexed in ES and already existed in MySQL DB we can run the command
```shell script
python manage.py enrich 
```

Or if we want to enrich specific trackhub(s) we can provide the hub url (one or many) as follows
```shell script
python manage.py enrich --huburl https://data.broadinstitute.org/compbio1/PhyloCSFtracks/trackHub/hub.txt ftp://ftp.vectorbase.org/public_data/rnaseq_alignments/hubs/aedes_aegypti/VBRNAseq_group_SRP039093/hub.txt 
```

Run the application

```shell script
python manage.py runserver
```

The app will be accessible at: http://127.0.0.1:8000

Create the super user (Optional)

```shell script
python manage.py createsuperuser
```


