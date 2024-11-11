"""
Updated by Fepe to Django 4.2
Django settings for WhoHePlayFor project.

Generated by 'django-admin startproject' using Django 1.9.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

from django.urls import reverse_lazy

# HEROKU
# import dj_database_url

TRUE_VALUES = ["true", "1", "t", "y", "yes"]

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "hi-there")
NEVERCACHE_KEY = os.environ.get("DJANGO_NEVERCACHE_KEY", "hi-there")


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", True) != "False"

if not DEBUG:
    ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "social_django",
    "graphene_django",
    "whpf",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "whoheplayfor.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                "whpf.context_processors.last_roster_update",
            ],
        },
    },
]

WSGI_APPLICATION = "whoheplayfor.wsgi.application"


# Database
DATABASES = {
    "default": {
        "ENGINE": os.environ.get(
            "POSTGRES_ENGINE",
            "django.db.backends.sqlite3",
        ),
        "NAME": os.environ.get("POSTGRES_DB", os.path.join(BASE_DIR, "db.sqlite3")),
        "USER": os.environ.get("POSTGRES_USER"),
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
    }
}

# HEROKU
# DATABASES['default'] = dj_database_url.config()


AUTHENTICATION_BACKENDS = [
    "social_core.backends.facebook.FacebookOAuth2",
    "social_core.backends.google.GoogleOAuth2",
    "social_core.backends.twitter.TwitterOAuth",
    "social_core.backends.reddit.RedditOAuth2",
    "django.contrib.auth.backends.ModelBackend",
]


# Password validation
AUTH_PASSWORD_VALIDATORS = []


# Internationalization
LANGUAGE_CODE = "en-us"

TIME_ZONE = "US/Eastern"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Heroku
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Static files (CSS, JavaScript, Images)
STATIC_URL = os.environ.get("STATIC_URL", "/static/")
STATIC_ROOT = os.environ.get("STATIC_ROOT", os.path.join(PROJECT_ROOT, "staticfiles"))

MEDIA_URL = os.environ.get("MEDIA_URL", "")
MEDIA_ROOT = os.environ.get("MEDIA_ROOT", "")


# LOGIN_URL = reverse_lazy("login")
LOGIN_URL = reverse_lazy("whpf:home")
LOGIN_REDIRECT_URL = reverse_lazy("whpf:home")
LOGOUT_REDIRECT_URL = reverse_lazy("whpf:home")

ADMINS = []
admin_names = os.environ.get("ADMIN_NAMES")
admin_emails = os.environ.get("ADMIN_EMAILS")
if admin_names and admin_emails:
    admin_names = admin_names.split(",")
    admin_emails = admin_emails.split(",")
    ADMINS = list(zip(admin_names, admin_emails))

EMAIL_ENABLED = os.environ.get("EMAIL_ENABLED", "False").lower() in TRUE_VALUES

if EMAIL_ENABLED:
    EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "False").lower() in TRUE_VALUES
    EMAIL_HOST = os.environ.get("EMAIL_HOST")
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT"))
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
    SERVER_EMAIL = os.environ.get("SERVER_EMAIL")  # Address for errors
    DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")  # For sendmail


SOCIAL_AUTH_ENABLED = os.environ.get("SOCIAL_AUTH_ENABLED", "False").lower() in TRUE_VALUES

if SOCIAL_AUTH_ENABLED:
    SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get("SOCIAL_AUTH_FACEBOOK_KEY")
    SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get("SOCIAL_AUTH_FACEBOOK_SECRET")

    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY")
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET")

    SOCIAL_AUTH_TWITTER_KEY = os.environ.get("SOCIAL_AUTH_TWITTER_KEY")
    SOCIAL_AUTH_TWITTER_SECRET = os.environ.get("SOCIAL_AUTH_TWITTER_SECRET")

    SOCIAL_AUTH_REDDIT_KEY = os.environ.get("SOCIAL_AUTH_REDDIT_KEY")
    SOCIAL_AUTH_REDDIT_SECRET = os.environ.get("SOCIAL_AUTH_REDDIT_SECRET")
    SOCIAL_AUTH_REDDIT_AUTH_EXTRA_ARGUMENTS = {"duration": "permanent"}

    SOCIAL_AUTH_REDIRECT_IS_HTTPS = True


# SENTRY
SENTRY_SDK_ENABLED = os.environ.get("SENTRY_SDK_ENABLED", "False").lower() in TRUE_VALUES

if SENTRY_SDK_ENABLED:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(dsn=os.environ.get("SENTRY_SDK_DSN"), integrations=[DjangoIntegration()])

# GRAPHENE

GRAPHENE = {
    "SCHEMA": "whpf.schema.schema",
}
