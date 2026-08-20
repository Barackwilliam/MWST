
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env_file(path=BASE_DIR / ".env"):
    
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_env_file()

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-badilisha-kabla-ya-production")
#: Chaguo-msingi ni production. Ukitaka kufanya kazi ndani ya kompyuta yako,
#: weka DEBUG=True kwenye environment yako ya ndani (si kwenye Render).
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

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
    # Lazima iwe KABLA ya LocaleMiddleware ili iondoe Accept-Language
    "core.middleware.DefaultSwahiliMiddleware",
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


_DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

if _DATABASE_URL:
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.parse(
            _DATABASE_URL,
            conn_max_age=600,
            ssl_require=_DATABASE_URL.startswith("postgres"),
        )
    }
else:
    # Fallback ya Supabase. TAZAMA: nywila hii ipo kwenye git history —
    # ibadilishe Supabase na uihamishie kwenye DATABASE_URL ya Render.
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


ID_PREFIX = os.environ.get("ID_PREFIX", "MUWESTA")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "[{asctime}] {levelname} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        # Malipo — muhimu kufuatilia pale mchango unapokwama `pending`.
        "finance": {"handlers": ["console"], "level": "INFO", "propagate": False},
        # Kelele isiyo na faida: kila SQL query ikiwa DEBUG=True.
        "django.db.backends": {"level": "WARNING"},
    },
}


# --- Pesapal ----------------------------------------------------------------
# SIRI HAZIANDIKWI HAPA. Weka kwenye environment ya Render:
#
#   PESAPAL_CONSUMER_KEY      = <kutoka Pesapal>
#   PESAPAL_CONSUMER_SECRET   = <kutoka Pesapal>
#   PESAPAL_ENV               = live  (au "sandbox" kwa majaribio)
#   PESAPAL_IPN_ID            = <kutoka `manage.py pesapal_ipn`>
#
# Funguo za merchant dashboard (pay.pesapal.com) ni za LIVE. Funguo za
# developer.pesapal.com ni za SANDBOX. Hazibadilishani — ukichanganya,
# Pesapal hujibu `invalid_consumer_key_or_secret_provided`.
#
# ONYO: PESAPAL_ENV=live inamaanisha PESA HALISI. Jaribu kwa kiasi kidogo.
#: `.strip()` inaondoa nafasi za ziada — `set VAR=thamani ` kwenye CMD ya
#: Windows hushika nafasi ya mwisho, na Pesapal hukataa funguo hiyo.
PESAPAL_CONSUMER_KEY = os.environ.get("PESAPAL_CONSUMER_KEY", "").strip()
PESAPAL_CONSUMER_SECRET = os.environ.get("PESAPAL_CONSUMER_SECRET", "").strip()
PESAPAL_ENV = os.environ.get("PESAPAL_ENV", "live").strip().lower()
PESAPAL_IPN_ID = os.environ.get("PESAPAL_IPN_ID", "").strip()


SITE_URL = (
    os.environ.get("SITE_URL")
    or os.environ.get("RENDER_EXTERNAL_URL")
    or "http://127.0.0.1:8000"
).strip().rstrip("/")


# DEBUG=True

if not DEBUG:
    if not SITE_URL.startswith("https://"):
        raise RuntimeError(
            f"SITE_URL si sahihi: {SITE_URL!r}. Lazima iwe anwani kamili ya "
            "https ya tovuti (mfano https://mwiso.onrender.com). Iweke kwenye "
            "Render > Environment. Pesapal hujenga callback na IPN kutoka "
            "hapo; ikiwa si sahihi, mtu aliyelipa hatarudi kwenye risiti yake."
        )
    if SITE_URL not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(SITE_URL)


CACHES = {"default": {
    "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    "LOCATION": "muwesta",
}}
