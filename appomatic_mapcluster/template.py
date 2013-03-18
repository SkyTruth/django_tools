# -*- coding: utf-8 -*-

def template_cluster_name(self, columns):
    return ""

def template_cluster_description(self, columns):
    return u"""Flare Detections: %(Temperature_avg)s°C (%(count)s detections)<br>
%(datetime_min)s - %(datetime_max)s<br>
%(latitude)sN %(longitude)sE<br>
<br>
Temp %(Temperature_avg)s°C (%(Temperature_min)s°C - %(Temperature_max)s°C)<br>
Magnitude %(RadiativeHeat_avg)sMW (%(RadiativeHeat_min)sMW - %(RadiativeHeat_max)sMW)<br>
<br>
Analysis by <a href="http://skytruth.org/">SkyTruth</a><br>
Data from <a href="http://www.ngdc.noaa.gov/dmsp/data/viirs_fire/viirs_html/download_viirs_fire.html">NOAA</a><br>
"""

def template_report_name(self, columns):
    return ""

def template_report_description(self, columns):
    return u"""<em style='white-space: nowrap;'>Flare Detection: %(Temperature)s°C @ %(SourceID)s:%(id)s</em><br>
%(datetime)s<br>
%(latitude)sN %(longitude)sE<br>
<br>
Temp %(Temperature)s°C<br>
Magnitude %(RadiativeHeat)sMW<br>
<br>
Analysis by <a href="http://skytruth.org/">SkyTruth</a><br>
Data from <a href="http://www.ngdc.noaa.gov/dmsp/data/viirs_fire/viirs_html/download_viirs_fire.html">NOAA</a><br>
"""
