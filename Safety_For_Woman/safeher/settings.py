"""
Woman For Safety Django settings.

Security notes
---------------
- All secrets (SECRET_KEY, Twilio credentials, email credentials) are read
  from environment variables. NOTHING sensitive is hard-coded or shipped
  to templates / the browser.
- Sensible secure defaults are applied automatically whenever DEBUG=False,
  which is what you should run in any real deployment.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    # Fallback ONLY for local dev / first `runserver`. Always set a real
    # secret via the environment before deploying anywhere.
    "dev-insecure-secret-key-change-me-before-deploying",
)

DEBUG = env_bool("DJANGO_DEBUG", default=True)

ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()
]

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Woman For Safety apps
    "core",
    "accounts",
    "facilities",
    "hotspots",
    "emergency",
    "moderation",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Custom: adds a couple of extra security headers (no JS involved).
    "core.middleware.SecurityHeadersMiddleware",
]

ROOT_URLCONF = "safeher.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_meta",
            ],
        },
    },
]

WSGI_APPLICATION = "safeher.wsgi.application"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
# For production, point this at Postgres instead, e.g. via DATABASE_URL +
# dj-database-url. SQLite is used here to keep the hackathon setup to
# "clone, migrate, run".

# ---------------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "auth.User"  # kept as Django's built-in User + Profile (see accounts.models)

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "core:dashboard"
LOGOUT_REDIRECT_URL = "core:home"

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-za"
TIME_ZONE = "Africa/Johannesburg"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Cache (used for rate limiting; swap LocMemCache -> Redis in production so
# limits are shared across worker processes)
# ---------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "safeher-ratelimit-cache",
    }
}

# ---------------------------------------------------------------------------
# Security hardening
# ---------------------------------------------------------------------------
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

# Session hygiene for a safety app: short idle timeout, always re-check.
SESSION_COOKIE_AGE = 60 * 30  # 30 minutes
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ---------------------------------------------------------------------------
# App Check-equivalent: since this is a server-rendered Django site (no
# public JSON API for a separate mobile client in this build), the
# meaningful equivalent of "App Check" is: every state-changing view
# requires a logged-in session + CSRF token that only our own rendered
# forms carry, plus the rate limiting in core/ratelimit.py.
# If a REST API for a future native app is added, put it behind DRF +
# drf-spectacular + a per-client signed attestation token here.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Third-party notification credentials (server-side ONLY, never exposed to
# templates or the client). See emergency/services.py.
# ---------------------------------------------------------------------------
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER", "")

# When True (the default, and always True in the hackathon demo) no real
# SMS/API calls are made -- notifications are only written to the
# ContactNotification log and the console. Flip to False + supply real
# Twilio credentials to go live.
WFS_DEMO_MODE = env_bool("WFS_DEMO_MODE", default=True)

# ---------------------------------------------------------------------------
# Woman For Safety domain configuration
# ---------------------------------------------------------------------------
# Bloemfontein bounding box used to project lat/lon onto the SVG safety map.
WFS_MAP_BOUNDS = {
    "lat_min": -29.16,
    "lat_max": -29.02,
    "lon_min": 26.05,
    "lon_max": 26.32,
}
WFS_GEOFENCE_RADIUS_KM = 0.6       # "approaching" distance for a warning
WFS_STANDDOWN_SECONDS = 60          # stand-down countdown length
WFS_REPORT_RATE_LIMIT = (3, 60 * 60)       # 3 reports / hour / user
WFS_PANIC_RATE_LIMIT = (5, 60 * 60)        # 5 panic activations / hour / user (abuse guard, never blocks the FIRST one)
WFS_CONTACT_RATE_LIMIT = (10, 60 * 60)     # 10 contact edits / hour / user

# ---------------------------------------------------------------------------
# Logging: moderation + security-relevant events always go to console
# (and, outside DEBUG, to a rotating file) so they can be audited.
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "[{asctime}] {levelname} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "loggers": {
        "wfs.security": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "wfs.moderation": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.security": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}