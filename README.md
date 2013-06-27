# Installation

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

Put this git repo at iuumapserver/src
Create a directory apps, and add symlinks to the appomatic-apps you want/need from this repo inside it. 
Create a directory apps/appomatic_settings, and inside it the empty files __app__.py and __init__.py. In addition, create a __settings__py containing your django database config. 

Run
  appomatic syncdb

Optionally run
  appomatic syncmapviews
  appomatic mapimport_exactearth
  appomatic mapimport_ksat

Then run
  appomatic runserver


# Summary of the various apps

## appomatic_alerts

Implementation of alerts.skytruth.org. Uses appomatic_feedserver, appomatic_mapserver and appomatic_legacymodels.

## appomatic_feedserver

Serves alerts as GeoRSS to users 

## appomatic_home

A very simple homepage listing in-house services. Right now pretty
much a hardcoded list of links.

## appomatic_legacymodels

Django model wrappers for all pre-existing tables in the SkyTruth
database. Does not contain any special logic, views or templates.

## appomatic_mapcluster

Generates clusters of map data for projects like VIIRS. Provides a
user interface to specify a date-range and generate and download
clusters for that date range.

## appomatic_mapdata

Models for AIS paths, SAR detections and VIIRS night fire detections.
Used in IUU project together with appomatic_mapserver.

## appomatic_mapdelta

A clone of appomatic_mapcluster to create heat maps instead of
clusters. Probably not that operational right now...

## appomatic_mapexport

Export maps from appomatic_mapdata in kml format (the old export tool
wrapped up as a django app)

## appomatic_mapfeed

Imports mapdata (same formats as supported by appomatic_mapserver)
into the feedentry table, to be served by the alerts framework.

## appomatic_mapimport

Import tools to import data into appomatic_mapdata from various
external sources.

## appomatic_mapserver

A generic framework for generating maps from database sources of
various formats. Maps can either be user defined (using django admin),
or hardcoded by other apps. Any sql query can be used as a data
source, and there is a set of different data formats supported
(linestrings/paths, simple points, points with a time component etc).
Supports templated output in geojson and kml format.

## appomatic_sitecontext

Provide the current site (base url) as a template variable.

## appomatic_siteinfo

The siteinfo (frackfinder) mapping project - a tool to display drill
sites, wells, events, suppliers, operators and chemicals. Uses
appomatic_mapserver with a custom template to display maps.

## appomatic_userena

Configures the userena signup/signin/signout user management framework

## appomatic_websitebase

Some base templates used in the IUU project

