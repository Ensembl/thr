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

# create a superuser defined by the environment variables
# Fix: 'Manager isn't available' error
# https://stackoverflow.com/a/67530965/4488332
echo "from django.contrib.auth import get_user_model;
User = get_user_model();
User.objects.filter(email='$DJANGO_ADMIN_EMAIL').delete();
User.objects.create_superuser('$DJANGO_ADMIN_USER', '$DJANGO_ADMIN_EMAIL', '$DJANGO_ADMIN_PASSWORD')" | python manage.py shell

exec "$@"