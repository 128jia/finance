"""
Django settings for stock_project project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
import json

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-i=vf1zu2*7%c841yfobjm^22y#72@d!kf-_xwmi7l$g=t&+q$&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tool',
    'monitor'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'distance_method.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # <--修改這裡！
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

WSGI_APPLICATION = 'distance_method.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
env = os.environ.get('PROJECT_ENV', 'dev')
if env == "prod":
    host = os.environ['USER_DB_HOST']
    database = os.environ['USER_DB_NAME']
    user = os.environ['USER_DB_USER']
    password = os.environ['USER_DB_PASSWORD']
    port = os.environ['USER_DB_PORT']

elif env == "dev":
    file_path = Path.cwd() / "config" / "correlation_db.json"
    with open (file_path, 'r')as f:
        db_info = json.load(f)
    host = db_info['USER_DB_HOST']
    database = db_info['USER_DB_NAME']
    user = db_info['USER_DB_USER']
    password = db_info['USER_DB_PASSWORD']
    port = db_info['USER_DB_PORT']
    
else:
    raise EnvironmentError("Unknown environment! Please set the 'ENV' variable to 'production' or 'development'.")


DATABASES = {
     'default': {

        'ENGINE': 'django.db.backends.postgresql_psycopg2',

        'NAME': database,

        'USER': user,

        'PASSWORD': password,

        'HOST': host,

        'PORT': port
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/


LANGUAGE_CODE = 'zh-Hant' #語言
TIME_ZONE = 'Asia/Taipei' #時區
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"] # <--修改這裡！

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

