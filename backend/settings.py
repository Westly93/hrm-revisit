from pathlib import Path
import environ
env = environ.Env()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
environ.Env.read_env(BASE_DIR / '.env')
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-(bivdx9bx7(kq^jr&uubi*9++&(dn)m53=e2llzex46-bl_b()'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', "localhost"]


# Application definition

INSTALLED_APPS = [

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    "adverts",
    "accounts",
    "contracts",
    # third party packages
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    "phonenumber_field",
    'django_browser_reload',
    'django_select2',
    "crispy_forms",
    "crispy_tailwind",
    'import_export',
    "django_htmx",
    'django_email_verification',
    'formtools',
    'easyaudit',

    'tailwind',
    "theme",
    "ckeditor",
    "django_countries",
]
""" CACHES = {
    # … default cache config and others
    "select2": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
} """

# Tell select2 which cache configuration to use:
# SELECT2_CACHE_BACKEND = "select2"
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    "django_htmx.middleware.HtmxMiddleware",
    'allauth.account.middleware.AccountMiddleware',
    'easyaudit.middleware.easyaudit.EasyAuditMiddleware',
    "django_browser_reload.middleware.BrowserReloadMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-',
             'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source'],
            ['Format', 'Styles', 'FontSize'],  # Added headings related buttons
        ],
        'width': 'full',
    }
}

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
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
        'HOST': env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT')
    }
}
# Google login
AUTHENTICATION_BACKENDS = (
    'allauth.account.auth_backends.AuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
)
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
LOGIN_REDIRECT_URL = '/'
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'EMAIL_AUTHENTICATION': True,
        'APP': {
            'client_id': "98447114892-ji44cfl0jon173s697a48ijelm5r0am4.apps.googleusercontent.com",
            'secret': "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",
            'key': env('SECRET_KEY')
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'westonmufudza@gmail.com'
EMAIL_HOST_PASSWORD = "ikqltoracpbopbcq"
EMAIL_USE_TLS = True
""" EMAIL_HOST = "localhost"
EMAIL_PORT = 1025
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = False """
# python -m smtpd -n -c DebuggingServer localhost:1025
# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
NPM_BIN_PATH = "C:/Program Files/nodejs/npm.cmd"

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

TAILWIND_APP_NAME = 'theme'
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"


# Django email verification settings
def email_verified_callback(user):
    user.is_active = True


def password_change_callback(user, password):
    user.set_password(password)


# Global Package Settings
EMAIL_FROM_ADDRESS = 'noreply@aliasaddress.com'  # mandatory
# mandatory (unless you use a custom link)
EMAIL_PAGE_DOMAIN = 'https://mydomain.com/'
EMAIL_MULTI_USER = False  # optional (defaults to False)

# Email Verification Settings (mandatory for email sending)
EMAIL_MAIL_SUBJECT = 'Confirm your email {{ user.username }}'
EMAIL_MAIL_HTML = 'mail_body.html'
EMAIL_MAIL_PLAIN = 'mail_body.txt'
EMAIL_MAIL_TOKEN_LIFE = 60 * 60  # one hour

# Email Verification Settings (mandatory for builtin view)
EMAIL_MAIL_PAGE_TEMPLATE = 'email_success_template.html'
EMAIL_MAIL_CALLBACK = email_verified_callback

# Password Recovery Settings (mandatory for email sending)
EMAIL_PASSWORD_SUBJECT = 'Change your password {{ user.username }}'
EMAIL_PASSWORD_HTML = 'password_body.html'
EMAIL_PASSWORD_PLAIN = 'password_body.txt'
EMAIL_PASSWORD_TOKEN_LIFE = 60 * 10  # 10 minutes

# Password Recovery Settings (mandatory for builtin view)
EMAIL_PASSWORD_PAGE_TEMPLATE = 'password_changed_template.html'
EMAIL_PASSWORD_CHANGE_PAGE_TEMPLATE = 'password_change_template.html'
EMAIL_PASSWORD_CALLBACK = password_change_callback
SOCIALACCOUNT_ADAPTER = 'accounts.adapters.CustomSocialAccountAdapter'
CRISPY_TEMPLATE_PACK = "tailwind"
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
INTERNAL_IPS = [
    "127.0.0.1",
]

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STATIC_URL = "static/"
LOGIN_REDIRECT_URL = "accounts:dashboard"
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
AUTH_USER_MODEL = "accounts.UserAccount"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"
CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"
INACTIVE_USER_THRESHOLD = 2
