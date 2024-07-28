from datetime import timedelta
from pathlib import Path
from environs import Env
import google.generativeai as genai


# Load environment variables from .env file
env = Env()
env.read_env()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

SITE_NAME = 'Pingoway'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', False)

ALLOWED_HOSTS = ["10.0.2.2","127.0.0.1", "localhost", ".vercel.app", "192.168.27.123"]
CORS_ALLOWED_ORIGINS = ['http://127.0.0.1']

STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "static/",
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    ##
    'django_cleanup.apps.CleanupConfig',#for files cleanup for each db update
    'profanity',#for bad world filter 
    # 3rd party
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    #'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'djoser',
    'social_django',
    'corsheaders',
    'djmoney',
    'djmoney.contrib.exchange',
    'address',
    'django_extensions',
    #'debug_toolbar',
    'django_celery_beat',
    'django_celery_results',
    'rosetta',
    'django_filters',
    'django.contrib.postgres',
    'service_objects',
    'modeltranslation',
    
    # pingoway apps
    'app_auth',
    'profiles',
    'tags',
    'services',
    'activities',
    'properties',
    'events',
    'reservations',
    'gemini',
]
EXCHANGE_BACKEND = 'djmoney.contrib.exchange.backends.OpenExchangeRatesBackend'
OPEN_EXCHANGE_RATES_APP_ID=env('OPEN_EXCHANGE_KEY')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "social_django.middleware.SocialAuthExceptionMiddleware",
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.locale.LocaleMiddleware'
]

ROOT_URLCONF = 'tourism.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

WSGI_APPLICATION = 'tourism.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': env('DB_DATABASE'),
        'NAME': env('DB_NAME'),
        "USER": env('DB_USER'),
        "HOST": env('DB_HOST'),
        "PORT": env('DB_PORT'),
        "PASSWORD": env('DB_PASSWORD')
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_USER_MODEL = "app_auth.User"

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


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=3),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('JWT',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

DJOSER = {
    'USER_CREATE_PASSWORD_RETYPE': True,
    'LOGIN_FIELD':'email',
    'SEND_ACTIVATION_EMAIL': True,
    'PASSWORD_RESET_CONFIRM_URL': 'auth/password/reset/confirm/{uid}/{token}',
    "ACTIVATION_URL": 'auth/activation/{uid}/{token}',
    'SERIALIZERS': {
        'user_create_password_retype': 'app_auth.serializers.pwUserCreateSerializer',
        'current_user': 'app_auth.serializers.UserSerializer',
    },
    'EMAIL': {
       'activation': 'app_auth.email.ActivationEmail',
       'password_reset': 'app_auth.email.PasswordResetEmail',
    },
    'PERMISSIONS': {
      'user_list': ['app_auth.permissions.CurrentUserOrAdmin']
    },
    "SOCIAL_AUTH_TOKEN_STRATEGY": "djoser.social.token.jwt.TokenStrategy",
    "SOCIAL_AUTH_ALLOWED_REDIRECT_URIS": ["http://127.0.0.1:3000"],
}




# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = env('TIME_ZONE')

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_HOST= env('EMAIL_HOST')
EMAIL_PORT= env('EMAIL_PORT')
EMAIL_HOST_USER= env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD= env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS= env('EMAIL_USE_TLS')
EMAIL_BACKEND= 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL= env('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env("GOOGLE_CLIENT_ID")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env("GOOGLE_SECRET")
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]
SOCIAL_AUTH_GOOGLE_OAUTH2_EXTRA_DATA = ["first_name", "last_name"]

AUTHENTICATION_BACKENDS = (
    'social_core.backends.open_id.OpenIdAuth',
    'app_auth.backends.pwGoogleOauth2',
    'social_core.backends.google.GoogleOAuth',
    'django.contrib.auth.backends.ModelBackend',
)

GOOGLE_API_KEY = None

# celery setting 
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TIMEZONE = env('TIME_ZONE')
CELERY_BROKER_URL = 'redis://127.0.0.1:6379'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_RESULT_EXTENDED = True

CELERY_BEAT_SCHEDULE = {
    'openexchange_update': {
        'task': 'profiles.tasks.update_openexchange_rates',
        'schedule': 60.0,
    },
}

USE_I18N = True

# Directories where Django will look for translation files
LOCALE_PATHS = (BASE_DIR / 'locale/', )


genai.configure(api_key=env("GEMINI_API_KEY"))

GEMINI_GENERATIVE_MODEL = env("GEMINI_GENERATIVE_MODEL")

MODELTRANSLATION_LANGUAGES = ('en', 'nl', 'ar', 'es', 'fr')

MODELTRANSLATION_FALLBACK_LANGUAGES = ('en', 'nl')

MODELTRANSLATION_AUTO_POPULATE = True