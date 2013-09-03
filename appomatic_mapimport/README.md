Django manage.py commands to import data into appomatic_mapdata from
various external sources. All of them uses a base class
appomatic_mapimport.mapimport.Import, or a subclass of it (like
appomatic_mapimport.seleniumimport.SeleniumImport).

The model appomatic_mapimport.models.Downloaded is used to keep track
of which files / pages have been imported already.

Note: The SeleniumImport based imports must run under an X server (for
example Xvfb), and have a FireFox profile configured. Especially note
that file download is tricky, and requires files of the mime type to
download, to download without a popup dialog / user interaction.

The selenium importer can optionally use http proxies (defined in the
database), and there is a script to scrape a list of available
proxies.
