# -*- coding: utf-8 -*-


def template_reports_name():
    return u"Detections"

def template_reports_description():
    return u'All detections'

def template_cluster_name(columns):
    return u"%(datetime_min)s: %(count)d detections, %(Temperature_avg).0f°C avg."

def template_cluster_description(columns):
    return u"""Flare Detections: %(Temperature_avg).0f°C (%(count)d detections)<br>
%(datetime_min)s - %(datetime_max)s<br>
%(latitude)sN %(longitude)sE<br>
<br>
Temp %(Temperature_avg).0f°C (%(Temperature_min).0f°C - %(Temperature_max).0f°C)<br>
Magnitude %(RadiativeHeat_avg)sMW (%(RadiativeHeat_min)sMW - %(RadiativeHeat_max)sMW)<br>
<br>
Analysis by <a href="http://skytruth.org/">SkyTruth</a><br>
Data from <a href="http://www.ngdc.noaa.gov/dmsp/data/viirs_fire/viirs_html/download_viirs_fire.html">NOAA</a><br>
"""

def template_report_name(columns):
    return u"%(datetime)s: %(Temperature).0f°C."

def template_report_description(columns):
    return u"""<em style='white-space: nowrap;'>Flare Detection: %(Temperature).0f°C @ %(SourceID)s:%(id)s</em><br>
%(datetime)s<br>
%(latitude)sN %(longitude)sE<br>
<br>
Temp %(Temperature).0f°C<br>
Magnitude %(RadiativeHeat)sMW<br>
<br>
Analysis by <a href="http://skytruth.org/">SkyTruth</a><br>
Data from <a href="http://www.ngdc.noaa.gov/dmsp/data/viirs_fire/viirs_html/download_viirs_fire.html">NOAA</a><br>
"""
