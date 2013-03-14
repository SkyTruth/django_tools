# -*- coding: utf-8 -*-

def template_report(self, columns):
    templates = {}

    templates['title'] = u'%(Temperature)s°C / %(RadiativeHeat)sMW'

    templates['summary'] = u"%(Temperature)s°C / %(RadiativeHeat)sMW @ %(latitude)sN %(longitude)sE, %(datetime)s"

    templates['content'] = u"""Flare Detection: %(Temperature)s°C<br>
%(datetime)s<br>
%(latitude)sN %(longitude)sE<br>
<br>
Temp %(Temperature)s°C<br>
Magnitude %(RadiativeHeat)sMW<br>
<br>
Analysis by <a href="http://skytruth.org/">SkyTruth</a><br>
Data from <a href="http://www.ngdc.noaa.gov/dmsp/data/viirs_fire/viirs_html/download_viirs_fire.html">NOAA</a><br>
"""

    templates['link'] = ''
    templates['kml_url'] = ''
    templates['tags'] = '{"viirs","noaa","nightfire"}'

    return templates
