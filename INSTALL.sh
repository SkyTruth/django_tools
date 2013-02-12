cd static/appomatic_mapserver

wget http://openlayers.org/download/OpenLayers-2.12.tar.gz
tar -xvzf OpenLayers-2.12.tar.gz
rm OpenLayers-2.12.tar.gz

wget http://jqueryui.com/resources/download/jquery-ui-1.10.0.custom.zip
unzip jquery-ui-1.10.0.custom.zip
mv jquery-ui-1.10.0.custom jquery-ui-1.10.0
rm jquery-ui-1.10.0.custom.zip


pip install geojson
pip install Shapely
curl https://raw.github.com/caolan/async/master/lib/async.js > async.js
wget http://stevenlevithan.com/assets/misc/date.format.js
