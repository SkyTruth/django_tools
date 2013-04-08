# -*- coding: utf-8 -*-

def template_reports_mangle_row(columns, row):
    if not row['Temperature']: row['Temperature'] = 0.0
    if not row['RadiativeHeat']: row['RadiativeHeat'] = 0.0

def template_reports_colorcolumn(columns):
    return u"Temperature"

def template_reports_colors(columns):
    # Colors are Alpha, Blue, Gree, Red (same order as KML)
    return {
        "mincolor": (255, 00, 255, 255),
        "maxcolor": (255, 00, 00, 255),
        "nonecolor": (255, 0, 255, 0)}

def template_reports_name():
    return u"Detections"

def template_reports_description():
    return u'All detections'

def template_clusters_mangle_row(columns, row):
    if not row['Temperature_avg']: row['Temperature_avg'] = 0.0
    if not row['Temperature_min']: row['Temperature_min'] = 0.0
    if not row['Temperature_max']: row['Temperature_max'] = 0.0
    if not row['RadiativeHeat_avg']: row['RadiativeHeat_avg'] = 0.0
    if not row['RadiativeHeat_min']: row['RadiativeHeat_min'] = 0.0
    if not row['RadiativeHeat_max']: row['RadiativeHeat_max'] = 0.0

def template_cluster_colorcolumn(columns):
    return u"Temperature_avg"

def template_cluster_colors(columns):
    # Colors are Alpha, Blue, Gree, Red (same order as KML)
    return {
        "mincolor": (255, 00, 255, 255),
        "maxcolor": (255, 00, 00, 255),
        "nonecolor": (255, 0, 255, 0)}

def template_cluster_name(columns):
    return u"%(count)d detections, %(Temperature_avg).0f°C"

def template_cluster_description(columns):
    return u"""
      <style>
        th, td {
          vertical-align: top;
          text-align: left;
          white-space: nowrap;
        }
      </style>
      <table>
        <tr><th>Location</th><td>%(latitude)sN %(longitude)sE</td></tr>
        <tr><th>Timeperiod</th><td>%(datetime_min)s - %(datetime_max)s</td></tr>
        <tr><th>Temperature (avg)</th><td>%(Temperature_avg).0f°C</td></tr>
        <tr><th>Temperature (min)</th><td>%(Temperature_min).0f°C</td></tr>
        <tr><th>Temperature (max)</th><td>%(Temperature_max).0f°C</td></tr>
        <tr><th>Magnitude (avg)</th><td>%(RadiativeHeat_avg).2fMW</td></tr>
        <tr><th>Magnitude (min)</th><td>%(RadiativeHeat_min).2fMW</td></tr>
        <tr><th>Magnitude (max)</th><td>%(RadiativeHeat_max).2fMW</td></tr>
      </table>
      <br>
      Analysis by <a href="http://skytruth.org/">SkyTruth</a><br>
      Data from <a href="http://www.ngdc.noaa.gov/dmsp/data/viirs_fire/viirs_html/download_viirs_fire.html">NOAA</a><br>
    """

def template_report_name(columns):
    return u"%(datetime)s: %(Temperature).0f°C."

def template_report_description(columns):
    return u"""
      <style>
        th, td {
          vertical-align: top;
          text-align: left;
          white-space: nowrap;
        }
      </style>
      <table>
        <tr><th>Location</th><td>%(latitude)sN %(longitude)sE</td></tr>
        <tr><th>Source</th><td>%(SourceID)s:%(id)s</td></tr>
        <tr><th>Time</th><td>%(datetime)s</td></tr>
        <tr><th>Temperature</th><td>%(Temperature).0f°C</td></tr>
        <tr><th>Magnitude</th><td>%(RadiativeHeat).2fMW</td></tr>
      </table>
      <br>
      Analysis by <a href="http://skytruth.org/">SkyTruth</a><br>
      Data from <a href="http://www.ngdc.noaa.gov/dmsp/data/viirs_fire/viirs_html/download_viirs_fire.html">NOAA</a><br>
    """
