#!/usr/bin/env python
# From http://trac.osgeo.org/openlayers/browser/trunk/openlayers/examples/proxy.cgi
# Modified for Django


"""This is a blind proxy that we use to get around browser
restrictions that prevent the Javascript from loading pages not on the
same server as the Javascript.  This has several problems: it's less
efficient, it might break some sites, and it's a security risk because
people can use this proxy to browse the web and possibly do bad stuff
with it.  It only loads pages via http and https, but it can load any
content type. It supports GET and POST requests."""

import urllib2
import cgi
import sys, os
import django.http
import django.core.exceptions
import django.views.decorators.csrf

HOP_HEADERS = set(('connection',
                   'keep-alive',
                   'proxy-authenticate',
                   'proxy-authorization',
                   'te',
                   'trailers',
                   'transfer-encoding',
                   'upgrade'))

# Designed to prevent Open Proxy type stuff.

allowedHosts = ['www.openlayers.org', 'openlayers.org', 
                'labs.metacarta.com', 'world.freemap.in', 
                'prototype.openmnnd.org', 'geo.openplans.org',
                'sigma.openplans.org', 'demo.opengeo.org',
                'www.openstreetmap.org', 'sample.azavea.com',
                'v2.suite.opengeo.org', 'v-swe.uni-muenster.de:8080', 
                'vmap0.tiles.osgeo.org', 'www.openrouteservice.org']

@django.views.decorators.csrf.csrf_exempt
def proxy(request):
    url = request.GET.get('url', "http://www.openlayers.org")

    host = url.split("/")[2]
    if allowedHosts and not host in allowedHosts:
        raise django.core.exceptions.PermissionDenied("This proxy does not allow you to access that location (%s)." % host)

    if not url.startswith("http://") or url.startswith("https://"):
        raise django.core.exceptions.PermissionDenied("Illegal request")

    if request.method == "POST":
        r = urllib2.Request(url, request.body, request.META)
        y = urllib2.urlopen(r)
    else:
        y = urllib2.urlopen(url)

    resp = django.http.HttpResponse(y.read(), status = y.getcode())
    info = y.info()
    for key in info:
        if key in HOP_HEADERS: continue # ignore hop-by-hop because django doesn't allow them anyway
        print key, "=", info[key]
        resp[key] = info[key]
    y.close()
    return resp
