#!/bin/sh
if [ "$DATABASE" = "mysql" ]
then
    echo "Waiting for mysql..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "MySQL started"
fi

# create the static files to be used by the Django admin portal
python manage.py collectstatic --noinput
# find and delete any remaining migration files before creating new ones
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
# migrate our current THR schema to the MySQL database
python manage.py makemigrations
python manage.py migrate

# build ES index
python manage.py search_index --rebuild -f

# create a superuser defined by the environment variables
python manage.py create_superuser --username "$DJANGO_ADMIN_USER" --password "$DJANGO_ADMIN_PASSWORD" --noinput --email "$DJANGO_ADMIN_EMAIL"

# import the assembly dump
python manage.py import_assemblies --fetch ena
# and load it to MySQL DB
python manage.py import_assemblies

exec "$@"