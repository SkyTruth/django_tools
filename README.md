# Installation

Set up a virtualenv

    virtualenv iuumapserver # or some other directory name where you want the installation
    cd iuumapserver
    source bin/activate
    root="$(pwd)"

Download and install latest development version of Django. Tested with Django==1.6.dev20130219095124

    mkdir $root/src
    cd $root/src
    git clone git://github.com/django/django.git
    cd django
    python setup.py install
    
Download and install this software

    cd $root/src
    git clone git@github.com:SkyTruth/django_tools.git
    pip install -r $root/src/django_tools/requirements.txt

    mkdir $root/apps
    cd $root/apps
    for x in ../src/django_tools/appomatic_*; do if [ "$x" = "../src/django_tools/appomatic_config" ]; then cp -r "$x" .; else ln -s $x; fi; done

Edit $root/apps/appomatic_config/__settings__.py to suit your database config and google accounts.

If you created a new database (not all functionality will work without our full dataset), run

    appomatic syncdb
    appomatic syncmapviews

Optionally run any of the data importers (you need to set up passwords for some of them to work)

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
