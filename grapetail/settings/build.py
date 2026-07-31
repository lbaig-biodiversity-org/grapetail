# Build-time settings used during `docker build` for steps that do not need
# a real database (e.g. `collectstatic`).  Keeping a SQLite backend here
# ensures the image can be built without a running MySQL server or the
# mysqlclient C extension being fully initialised.
#
# These settings are NOT used at runtime — the container CMD continues to
# use the production / local settings via DJANGO_SETTINGS_MODULE.

from .base import *  # noqa: F401, F403

# A dummy key is sufficient for collectstatic; it is never used in production.
SECRET_KEY = "build-only-not-a-secret-key-do-not-use-in-production"

# Force SQLite so no MySQL driver is imported during image build.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "/tmp/build.sqlite3",
    }
}
