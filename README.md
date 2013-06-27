virtualenv iuumapserver # or some other directory name where you want the installation
cd iuumapserver
source bin/activate

Download and install latest development version of Django. Tested with Django==1.6.dev20130219095124

pip install the following:

Shapely==1.2.17
appomatic==0.0.14
appomatic-admin==0.0.14
appomatic-appadmin==0.0.14
appomaticcore==0.0.15
bitstring==3.0.2
distribute==0.6.24
fastkml==0.3dev
geojson==1.0.1
paramiko==1.9.0
psycopg2==2.4.6
pycrypto==2.6
pygeoif==0.3.1dev
python-dateutil==2.1
simplejson==3.0.7
six==1.2.0

Put this git repo at iuumapserver/apps
Copy any __settings__.py.template to __settings__.py and edit.
Run

appomatic syncdb
appomatic syncmapviews
appomatic mapimport_exactearth
appomatic mapimport_ksat
appomatic runserver
