"""
.. See the NOTICE file distributed with this work for additional information
   regarding copyright ownership.
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import os
from datetime import timedelta
from pathlib import Path

# pylint: disable=pointless-string-statement
"""
Django settings for thr project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

# TODO: take a look at the checklist
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR her is 'thr/thr'
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

# Get Django environment set by docker (i.e either development or production), or else set it to local
DJANGO_ENV = os.environ.get('DJANGO_ENV', 'local')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'changeme')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.environ.get('DEBUG', 0)))

# it will be set depending on the environement
ALLOWED_HOSTS = []

# If Django environement has been set by docker it would be either development
# or production otherwise it would be undefined or local
if DJANGO_ENV == 'development':
    DEBUG = True
    ALLOWED_HOSTS = ['127.0.0.1', '0.0.0.0', 'localhost']

elif DJANGO_ENV == 'production':
    ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'users.apps.UsersConfig',
    'trackhubs.apps.TrackhubsConfig',
    'search.apps.SearchConfig',
    'stats.apps.StatsConfig',
    'trackdbs.apps.TrackdbsConfig',
    'info.apps.InfoConfig',
    # Django Elasticsearch integration
    'django_elasticsearch_dsl',
    # Django REST framework Elasticsearch integration
    'django_elasticsearch_dsl_drf',
    'django_mysql',
    'django_crontab',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5,
    'ORDERING_PARAM': 'ordering',
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'thr.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # TODO: change later after adding react frontend
        'DIRS': [BASE_DIR / '../templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'thr.wsgi.application'

# https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#substituting-a-custom-user-model
AUTH_USER_MODEL = 'users.CustomUser'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.mysql'),
        'NAME': os.environ.get('DB_DATABASE', 'thr_db'),
        'USER': os.environ.get('DB_USER', 'thr_dev'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'password'),
        'HOST': os.environ.get('DB_HOST', 'mysql'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
}

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': os.environ.get('ES_HOST', 'elasticsearch:9200'),
        'timeout': 60000,  # Custom timeout
    },
}

# Name of the Elasticsearch index
ELASTICSEARCH_INDEX_NAMES = {
    'search.documents': os.environ.get('ES_INDEX', 'trackhubs'),
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Logging
# https://docs.djangoproject.com/en/2.2/topics/logging/
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'thr.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'propagate': True,
        },
        'trackhubs.parser': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG'
        }
    }
}

# Set email verification access token lifetime to 30 minutes (default is 5 minutes)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
}

# cron job scheduled to be run at 00:00 every Sunday
CRONJOBS = [
    ('0 0 * * SUN', 'thr.trackdbs.update_status.update_all_trackdbs', '>> ../../thr.log')
]

# redirect errors to stdout
CRONTAB_COMMAND_SUFFIX = '2>&1'

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# (CORS) Cross-Origin Resource Sharing Settings
CORS_ORIGIN_ALLOW_ALL = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

# We add the variable STATIC_ROOT which defines where the static files are collected in the production build
# when the command 'python manage.py collectstatic --noinput' is run from the 'entrypoint.sh' file,
# otherwise this command would not run.
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'thr_home'
LOGIN_URL = 'login'

# this can be tested locally using the command:
# python -m smtpd -n -c DebuggingServer localhost:1025
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 1025)

FRONTEND_URL = os.environ.get('FRONTEND_URL', 'localhost:3000')
BACKEND_URL = os.environ.get('BACKEND_URL', 'localhost:8000')

# The number of elements shown in Species, Assembly
# and Hub facets can be controlled using FACETS_LENGHT
FACETS_LENGHT = 30

# The hub check API is in a separate VM
HUBCHECK_API_URL = os.environ.get('HUBCHECK_API_URL', 'http://localhost:8888/hubcheck')

# Whether to append trailing slashes to URLs.
APPEND_SLASH = False

THR_VERSION = "0.8.1"
