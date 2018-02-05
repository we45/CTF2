"""
Django settings for hospital project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

CSRF_COOKIE_NAME = 'java_csrf'
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9)59wm8ize35ahv9t146!8d3dzmstp%tx^sd9iv$3fezwn+d*_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['*']

SITE_ID=1
# Application definition

LOGIN_REDIRECT_URL = '/login/'

LOGIN_URL = '/login/'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'hospital.urls'

WSGI_APPLICATION = 'hospital.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'hospital_db',
#         'USER': 'root',
#         'PASSWORD': 'hegemony86'
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'hospital_db',
        'USER': 'postgres',
        # 'PASSWORD': 'we45#secdevops@2016',
        'PASSWORD': 'hegemony86',
	    # 'PASSWORD': 'prakash@we45',
        'HOST': '127.0.0.1',        
        'PORT': '',
    }
}


INSTALLED_APPS = (
    # 'django.contrib.admin',
    # 'django.contrib.auth',
    # 'django.contrib.contenttypes',
    # 'django.contrib.sessions',
    # 'django.contrib.messages',
    # 'django.contrib.staticfiles',
    # 'django.contrib.sites'
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # 'eventlog',
    'tastypie',
    'ctf',
)
# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

EMAIL_HOST = 'smtp.mandrillapp.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'abhay@we45.com'
EMAIL_HOST_PASSWORD = 'zEY7HTM6BNq4KaSytEsZ0Q'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/


STATIC_URL = '/static/'
MEDIA_URL = '/media/'
AUTH_USER_MODEL = 'ctf.User'
STATIC_ROOT = os.path.join(os.path.dirname(__file__), '../ctf/static/')
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), '../ctf/media/')

ES_PATH = 'http://127.0.0.1:9200'

ZAP = {
    "ip": "192.168.1.135",
    "port" : "8090",
}

SYSTEM_IP = 'http://192.168.1.103:8000'

# SECURE_BROWSER_XSS_FILTER  = True
