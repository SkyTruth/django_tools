import appomatic_mapserver.maptemplates

class MapTemplate(appomatic_mapserver.maptemplates.MapTemplateSimple):
    name = "SkyTruth Alerts"

    #    1 | NRC = toxic materials release, pollution event
    #    2 | SkyTruth = published by Skytruth - we have a nice logo-pushpin so we can keep that
    #    3 | NOAA = NOAA investigation  - generally of a pullution event - have a nice logo marker already
    #    4 | PA DEP Permit = permit issued (no acutal even on the ground)
    #    5 | PA DEP SPUD = drillinng started
    #    6 | USGS Earthquakes = Earthquakes (of course)
    #    7 | WV DEP Permit Issued = permit issued (no acutal even on the ground)
    #    8 | WV DEP Permit Activity
    #    9 | PA DEP Permit Violation = citation issued, may or may not be any real event on the ground
    #   10 | FracFocus = fracking event
    # 1001 | GOGIS = need to split this one up actually, there are both spills and violations from Colorado, so we should differentiate
    # 1002 | viirs = Night fire / flare  detection

    source_icons = {
        1: "http://alerts.skytruth.org/markers/chemleak.png",
        2: "http://alerts.skytruth.org/markers/st_google_marker4a.png",
        3: "http://alerts.skytruth.org/markers/NOAA_marker.png",
        4: "http://alerts.skytruth.org/markers/permit.png",
        5: "http://alerts.skytruth.org/markers/drill.png",
        6: "http://alerts.skytruth.org/markers/earthquake.png",
        7: "http://alerts.skytruth.org/markers/permit.png",
        8: "http://alerts.skytruth.org/markers/drill.png",
        9: "http://alerts.skytruth.org/markers/permit-broken.png",
        10: "http://alerts.skytruth.org/markers/fracking.png",
        1001: "http://alerts.skytruth.org/markers/chemleak.png",
        1002: "http://alerts.skytruth.org/markers/nightfire.png"
        }

    def row_generate_text(self, row):
        row['name'] = ""
        row['iconWidth'] = 32
        row['iconHeight'] = 32
        
        row['description'] = row['content']

        row['style'] = {
          "fillOpacity": 1.0,
          "fillColor": "#0000ff",
          "strokeOpacity": 1.0,
          "strokeColor": "#ff0000",
          "strokeWidth": 1,
          "pointRadius": 3,
          "externalGraphic": self.source_icons[row['source_id']],
          "graphicWidth": 32,
          "graphicHeight": 32
          }
    
