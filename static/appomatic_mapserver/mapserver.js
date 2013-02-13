var map, data, layerdefs;

var MapServer = {};
MapServer.Layer = {};
MapServer.Format = {};
MapServer.Protocol = {};

MapServer.Layer.Db = OpenLayers.Class(OpenLayers.Layer.Vector, {
  CLASS_NAME: "MapServer.Layer.Db",

  setTimeRange: function(min, max) {
    this.minfilter.value = min;
    this.maxfilter.value = max;

    this.filterStrategy.setFilter(this.filter);
    this.refresh({force:true});
  },

  initialize: function(name, options) {

    this.minfilter = new OpenLayers.Filter.Comparison({
      type: OpenLayers.Filter.Comparison.GREATER_THAN_OR_EQUAL_TO,
      property: "datetime",
      value: 0,
    });
    this.maxfilter = new OpenLayers.Filter.Comparison({
      type: OpenLayers.Filter.Comparison.LESS_THAN_OR_EQUAL_TO,
      property: "datetime",
      value: 0,
    });
    this.filter = new OpenLayers.Filter.Logical({
      type: OpenLayers.Filter.Logical.AND,
      filters: [this.minfilter, this.maxfilter]
    });
    this.filterStrategy = new OpenLayers.Strategy.Filter({filter: this.filter, caching: false});

    OpenLayers.Util.extend(options, {
      projection: new OpenLayers.Projection("EPSG:4326"), // Same as WGS84
      strategies: [
        new OpenLayers.Strategy.BBOX({resFactor: 1}),
        this.filterStrategy
      ],
      protocol: new OpenLayers.Protocol.HTTP(
        OpenLayers.Util.extend(options.protocol, {
          url: MapServer.apiurl,
          format: new OpenLayers.Format.GeoJSON(),
          params: OpenLayers.Util.extend(options.protocol.params, {
            action:'map'}),
        })),
      styleMap: new OpenLayers.StyleMap({
        "default": new OpenLayers.Style({
          graphicName: "circle",
          pointRadius: 3,
          fillOpacity: 0.25,
          fillColor: "#ffcc66",
          strokeColor: "#ff9933",
          strokeWidth: 1
        })
      }),
      renderers: ["Canvas", "SVG", "VML"]
    });
    OpenLayers.Layer.Vector.prototype.initialize.apply(this, [name, options]);
  },
  eventListeners:{
    'featureselected':function(evt) {
      var feature = evt.feature;
      var attrs = feature.attributes;

      if (feature.popup) return;

      if (attrs.mmsi) {
        if (!attrs.url) {
          attrs.url = "http://www.marinetraffic.com/ais/shipdetails.aspx?MMSI=" + attrs.mmsi
        }
        if (!attrs.name) {
          attrs.name = attrs.mmsi;
        }
      }
      var popup = new OpenLayers.Popup.FramedCloud("popup",
        new OpenLayers.LonLat(feature.geometry.bounds.right, feature.geometry.bounds.bottom),
        null,
        Mustache.render("<h2><a href='{{url}}'>{{name}}</a></h2><table><tr><th>MMSI</th><td>{{mmsi}}</td></tr><tr><th>Type</th><td>{{type}}</td></tr><tr><th>Length</th><td>{{length}}</td></tr></table>", attrs),
        null,
        true
      );
      feature.popup = popup;
      map.addPopup(popup);
    },
    'featureunselected':function(evt){
      var feature = evt.feature;
      map.removePopup(feature.popup);
      feature.popup.destroy();
      feature.popup = null;
    }
  }
});     

MapServer.Format.KML = OpenLayers.Class(OpenLayers.Format.KML, {
  CLASS_NAME: "MapServer.Format.KML",
  parseStyle: function(node) {
    var baseURI = node.baseURI.split("?")[0]; // remove query, if any
    if (baseURI.lastIndexOf("/") != baseURI.length - 1) {
      baseURI = baseURI.substr(0, baseURI.lastIndexOf("/") + 1);
    }
    var style =  OpenLayers.Format.KML.prototype.parseStyle.call(this, node);
    if (typeof style.externalGraphic != "undefined" && style.externalGraphic.match(new RegExp("(^/)|(://)")) == null) {
      style.externalGraphic = baseURI + style.externalGraphic;
    }
    return style;
  }
});

MapServer.Protocol.MultiHTTP = OpenLayers.Class(OpenLayers.Protocol.HTTP, {
  datasets: [], // [{url:"",params:{}}]
  read: function(options) {
    var self = this;
    var response = null;
    async.each(
      this.datasets,
      function (item, cb) {
        suboptions = OpenLayers.Util.extend(OpenLayers.Util.extend({}, options), item);
        suboptions.scope = self;
        suboptions.callback = function (resp) {
          if (response && resp.features) {
            response.features = response.features.concat(resp.features);
          } else if (resp.features) {
            response = resp;
          }
          cb();
        };
        OpenLayers.Protocol.HTTP.prototype.read.call(self, suboptions);
      },
      function (err) {
        if (!response) {
          response = {code: OpenLayers.Protocol.Response.FAILURE};
        }
        options.callback.call(options.scope, response);
      }
    );
  }
});

MapServer.Layer.KmlDateDir = OpenLayers.Class(OpenLayers.Layer.Vector, {
  CLASS_NAME: "MapServer.Layer.KmlDateDir",

  setTimeRange: function(min, max) {
    var epochToDate = function (e) { d = new Date(0); d.setUTCSeconds(e); return d; }

    datasets = [];
    for (t = min; t <= max + 24 * 60 * 60; t += 24*60*60) {
       datasets.push({url: MapServer.fileurl + "vessel-detections/" + epochToDate(t).format("UTC:yyyy-mm-dd") + "/doc.kml"});
    }
    this.protocol.datasets = datasets;

    this.refresh({force:true});
  },

  initialize: function(name, options) {
    OpenLayers.Util.extend(options, {
      projection: new OpenLayers.Projection("EPSG:4326"), // Same as WGS84
      strategies: [new OpenLayers.Strategy.Fixed()],
      protocol: new MapServer.Protocol.MultiHTTP(
        OpenLayers.Util.extend(options.protocol, {
          format: new MapServer.Format.KML({
            extractStyles: true, 
            extractAttributes: true,
            maxDepth: 1024
          }),
        })
      ),
      renderers: ["Canvas", "SVG", "VML"]
    });
    OpenLayers.Layer.Vector.prototype.initialize.apply(this, [name, options]);
  }
});


MapServer.init = function () {
  async.series([
    function(cb) {
      map = new OpenLayers.Map('map', {
        controls: [
          new OpenLayers.Control.Navigation(),
          new OpenLayers.Control.PanZoomBar(),
          new OpenLayers.Control.LayerSwitcher({'ascending':false}),
          new OpenLayers.Control.Permalink(),
          new OpenLayers.Control.ScaleLine(),
          new OpenLayers.Control.Permalink('permalink'),
          new OpenLayers.Control.MousePosition(),
          new OpenLayers.Control.OverviewMap(),
          new OpenLayers.Control.KeyboardDefaults()
        ],
        setTimeRange: function (min, max) {
          $.each(this.layers, function () {
            if (typeof this.setTimeRange != "undefined") {
              this.setTimeRange(min, max);
            }
          });
        }
      });

      map.addLayer(new OpenLayers.Layer.OSM("Simple OSM Map"));

      map.setCenter(
        new OpenLayers.LonLat(-118.20782, -24.9335916667).transform(
          new OpenLayers.Projection("EPSG:4326"),
          map.getProjectionObject()
        ), 5
      );

      cb();
    },

    function(cb) {
      $.get(
        MapServer.apiurl,
        {action: 'layers'},
        function(d) { layerdefs = d; cb(); },
        "json");
    },

    function(cb) {
      $.each(layerdefs, function (key, value) {
         var constr = eval(value.type);
         var layer = new constr(key, value.options);
         map.addLayer(layer);

         map.addControl(new OpenLayers.Control.SelectFeature(layer, {
           clickout: true,
           hover: false,
           autoActivate: true
         }));
      });

      cb();
    },

    function(cb) {
      $.get(
        MapServer.apiurl,
         {action: 'timerange'},
         function(d) { data = d; cb(); },
         "json"
      );
    },

    function(cb) {
      map.setTimeRange(data.timemax-24*60*60, data.timemax);

      $("#time-slider").slider({
        range: true,
        min: data.timemin,
        max: data.timemax,
        values: [data.timemax-24*60*60, data.timemax],
        stop: function(event, ui) {
          map.setTimeRange(ui.values[0], ui.values[1]);
        }
      });
    }
  ]);
};
