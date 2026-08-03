"""
MWST MMS — Django settings
Hatua ya sasa: FRONTEND ONLY (mock data). Hakuna database bado.
Tukianza backend: ongeza DATABASES + INSTALLED_APPS za models.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-badilisha-kabla-ya-production")
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")
CSRF_TRUSTED_ORIGINS = [
    o for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    "core",
    "accounts",
    "geo",
    "members",
    "finance.apps.FinanceConfig",
    "programs",
    "content",
]

AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "/ingia/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.template.context_processors.csrf",
        "django.template.context_processors.i18n",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "core.context_processors.brand",
    ]},
}]

# --- Database ---------------------------------------------------------------
# Ndani: SQLite.  Render/Supabase: weka DATABASE_URL kwenye env.
# DATABASE_URL = os.environ.get("DATABASE_URL", "")
# if DATABASE_URL:
#     import dj_database_url
#     DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600,
#                                                   ssl_require=True)}
# else:
#     DATABASES = {
#         "default": {
#             "ENGINE": "django.db.backends.sqlite3",
#             "NAME": BASE_DIR / "db.sqlite3",
#         }
#     }


#Database e.madventure29@gmail.com
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres', 
        'USER': 'postgres.vgosiffobeoohticeuro',  
        'PASSWORD': 'Nyumbachap@123', 
        'HOST': 'aws-0-eu-west-3.pooler.supabase.com', 
        'PORT': '5432',
        'OPTIONS': {'sslmode': 'require'},  # hii inaruhusu SSL


    }
}


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"

# --- i18n: Kiswahili ndiyo default, Kiingereza ni ya pili -------------------
LANGUAGE_CODE = "sw"
LANGUAGES = [("sw", "Kiswahili"), ("en", "English")]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Africa/Dar_es_Salaam"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Usalama (huwashwa production) -----------------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"


# ===========================================================================
#  USALAMA (production tu)
# ===========================================================================
# Vinawaka pale DEBUG=False. Ndani ya kompyuta yako (DEBUG=True) havisumbui.
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000          # mwaka mmoja
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_HTTPONLY = True
    X_FRAME_OPTIONS = "DENY"
    SESSION_EXPIRE_AT_BROWSER_CLOSE = False
    SESSION_COOKIE_AGE = 60 * 60 * 8        # saa 8

    CSRF_TRUSTED_ORIGINS = [
        f"https://{h.lstrip('.')}" for h in ALLOWED_HOSTS if h not in ("*", "")
    ] + ["https://*.onrender.com"]

# Onyo la mapema: SECRET_KEY ya mfano isitumike production
if not DEBUG and SECRET_KEY.startswith("django-insecure-"):
    raise RuntimeError(
        "SECRET_KEY ya mfano haiwezi kutumika production. "
        "Weka SECRET_KEY halisi kwenye environment variables."
    )


# ===========================================================================
#  BARUA PEPE
# ===========================================================================
# Bila SMTP, barua pepe zinachapishwa kwenye console (nzuri kwa maendeleo).
# Production: weka EMAIL_HOST na wenzake kwenye environment variables.
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
if EMAIL_HOST:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
    EMAIL_USE_TLS = True
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "info@muslimwelfare.or.tz")
