## TrackHub Registry

TrackHub Registry (THR) is a global centralised collection of publicly accessible [track hubs](http://genome.ucsc.edu/goldenPath/help/hgTrackHubHelp.html#Intro). The goal of the project is to allow third parties to advertise track hubs, and to make it easier for researchers around the world to discover and use track hubs containing different types of genomic research data.

This repository is created to give the project a technology refresh while keeping the same core functionalities.

### Prerequisites

* Python 3.7+
* venv
* Docker and Docker-compose are required if you want to use docker containers

### Local deployment

Clone the project

```shell script
git clone https://github.com/Ensembl/thr.git
cd thr
```

#### Using Docker

First, we need to run a DB migration using the command

```shell script
docker-compose run web python manage.py migrate
```

This will run the database migration and set up all the tables that are required for our project in the new MySQL database

Next, we fire up docker-compose

```shell script
docker-compose up
```

The app will be accessible at: http://127.0.0.1:8000

To stop the docker application use:

```shell script
docker-compose stop
```

To removes stopped service containers and anonymous volumes attached use:

```shell script
docker-compose rm -v
```

##### Create super user (Optional)

Get the container ID 

```shell script
docker container ls
```

Then run the command

```shell script
docker exec -it <container_id> python manage.py createsuperuser
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
export DEBUG=1
export THR_DB_NAME=thr_users  # The DB should already be created
export THR_DB_USER=user
export THR_DB_PASSWORD=password
export THR_HOST=localhost
export THR_PORT=3306
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


