# -*- coding: utf-8 -*-

def template_cluster_name( columns):
    return ""

def template_cluster_description(columns):
    return u"""Flare Detections: %(Temperature_avg)s°K (%(count)s detections)<br>
%(datetime_min)s - %(datetime_max)s<br>
%(latitude)sN %(longitude)sE<br>
<br>
Temp %(Temperature_avg)s°K (%(Temperature_min)s°K - %(Temperature_max)s°K)<br>
Magnitude %(RadiativeHeat_avg)sMW (%(RadiativeHeat_min)sMW - %(RadiativeHeat_max)sMW)<br>
<br>
Analysis by <a href="http://skytruth.org/">SkyTruth</a><br>
Data from <a href="http://www.ngdc.noaa.gov/dmsp/data/viirs_fire/viirs_html/download_viirs_fire.html">NOAA</a><br>
"""

def template_report_name(columns):
    return ""

def template_report_description(columns):
    return u"""<em style='white-space: nowrap;'>Flare Detection: %(Temperature)s°K @ %(SourceID)s:%(id)s</em><br>
%(datetime)s<br>
%(latitude)sN %(longitude)sE<br>
<br>
Temp %(Temperature)s°K<br>
Magnitude %(RadiativeHeat)sMW<br>
<br>
Analysis by <a href="http://skytruth.org/">SkyTruth</a><br>
Data from <a href="http://www.ngdc.noaa.gov/dmsp/data/viirs_fire/viirs_html/download_viirs_fire.html">NOAA</a><br>
"""
