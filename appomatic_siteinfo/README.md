SiteInfo is a database of sites (geographic locations with metadata),
wells (drill holes at sites) and events at those sites / weells, as
well as some related entities (operators, suppliers, chemicals).

It uses appomatic_mapserver to generate maps of sites and wells,
Django Haystack for search, and
https://github.com/redhog/appomatic_renderable for rendering /
templating and linking to objects.

Note: To understand which templates are used to render what, please read the documentation for appomatic_renderable!

For mapserver, it provides its own BuiltinApplication, with its own
template.
