import os.path

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'HOST': 'localhost',
        'NAME': 'skytruth',
        'USER': 'skytruth',
        'PASSWORD': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    }
}
TOLERANCE_BASE_MAX = 20
TOLERANCE_BASE_MIN = -11 # 2**-11 degrees ~= 50 meters, the resolution of GPS
USE_TZ=True
DEBUG=True

GOOGLE_MAPSENGINE_EMAIL="XXXXXXXXXXXXX@developer.gserviceaccount.com"
GOOGLE_MAPSENGINE_KEY=os.path.join(VIRTUALENV_DIR, "key.p12")
GOOGLE_MAPSENGINE_APIURL="https://www.googleapis.com/auth/mapsengine"

GOOGLE_MAPS_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

SITEINFO_GOOGLE_MAPSENGINE_LAYER = "XXXXXXXXXXXXXXXXXXXX-XXXXXXXXXXXXXXXXXXXX"
