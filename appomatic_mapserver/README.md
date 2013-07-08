A request for a map contains two basic pieces of information:

* An application name
* An output format name

The output format select a map renderer (a subclass of
appomatic_mapserver.maprenderers.MapRenderer).

The application name selects an application (a subclass of
appomatic_mapserver.models.BaseApplication). These can either be
instances of the appomatic_mapserver.models.Application django model,
defined in the database, or subclasses of
appomatic_mapserver.models.BuiltinApplication defined in some other
django app.

Regardless of how the application is defined, it specifies a set of
layers (instances of appomatic_mapserver.models.BaseLayer). Each layer
has a query (SQL query), a backend type / map source, a template, and
a json structure for the client side.

The map source selects a class to use to get map data from the
database using the query (a subclass of
appomatic_mapserver.mapsources.MapSource). This is used to do
clustering, filter for date ranges, generate simplified paths etc.

The template selects a class to render map items text and styling (esp
for kml output) (a subclass of
appomatic_mapserver.maptemplates.MapTemplate).

So, to sum this up, this is the stack of instances used to serve up a map:

* MapRenderer
* BaseApplication
* BaseLayer (1 or more)
  * MapSource
  * MapTemplate
