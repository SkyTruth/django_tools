var map, data, layerdefs;

$.widget("ui.betterslider", $.ui.slider, {
  _mouseCapture: function(event) {
    var self = this;
    if ($(event.target).hasClass("ui-slider-range")) {
      this.elementSize = {
        width: this.element.outerWidth(),
        height: this.element.outerHeight()
      };
      this.elementOffset = this.element.offset();
      self._handleIndex = -1;
      self._rangeStartMouseValue = self._normValueFromMouse({x:event.pageX, y:event.pageY});
      self._rangeStartValues = self.values();
      return true;
    } else {
      return $.ui.slider.prototype._mouseCapture.apply(this, arguments);
    }
  },
  _slide: function(event, index, newVal) {
    var self = this;
    if (index == -1) {
      self.values(self._rangeStartValues.map(function (v) {
        return v + newVal - self._rangeStartMouseValue;
      }));
    } else {
      $.ui.slider.prototype._slide.apply(self, arguments);
    }
  }
});


var MapServer = {};
MapServer.Layer = {};
MapServer.Format = {};
MapServer.Protocol = {};
MapServer.Control = {};

MapServer.TIME_FORMAT = "UTC:yyyy-mm-dd HH:MM:ss";
MapServer.DATE_FORMAT = "UTC:yyyy-mm-dd";

MapServer.getJsonFromUrl = function() {
  var query = location.search.substr(1);
  var data = query.split("&");
  var result = {};
  for(var i=0; i<data.length; i++) {
    var item = data[i].split("=");
    result[item[0]] = item[1];
  }
  return result;
}

MapServer.epochToDate = function (e) {
  d = new Date(0);
  d.setUTCSeconds(e);
  return d;
}

MapServer.dateTimeToDate = function (d) {
  return new Date(d.getFullYear(), d.getMonth(), d.getDate());
}

MapServer.Control.Menu = OpenLayers.Class(OpenLayers.Control, {
  CLASS_NAME: "MapServer.Control.Menu",
  minimizeDiv: null,
  maximizeDiv: null,
  contentDiv: null,

  initialize: function(options) {
    OpenLayers.Control.prototype.initialize.apply(this, arguments);
  },

  destroy: function() {
    this.map.events.un({buttonclick: this.onButtonClick, scope: this});
    this.events.unregister("buttonclick", this, this.onButtonClick);
    OpenLayers.Control.prototype.destroy.apply(this, arguments);
  },

  setMap: function(map) {
    OpenLayers.Control.prototype.setMap.apply(this, arguments);
    this.map.events.register("buttonclick", this, this.onButtonClick);
  },

  draw: function() {
    OpenLayers.Control.prototype.draw.apply(this);
    this.loadContents();
    this.minimizeControl();
    this.redraw();    
    return this.div;
  },

  onButtonClick: function(evt) {
    var button = evt.buttonElement;
    if (button === this.minimizeDiv) {
      this.minimizeControl();
    } else if (button === this.maximizeDiv) {
      this.maximizeControl();
    } else if (button._layerSwitcher === this.id) {
      if (button["for"]) {
        button = document.getElementById(button["for"]);
      }
      if (!button.disabled) {
        console.log(button);
      }
    }
  },


  redraw: function() {
    return this.div; 
  },

  maximizeControl: function(e) {
    this.div.style.width = "";
    this.div.style.height = "";

    this.showControls(false);

    if (e != null) {
      OpenLayers.Event.stop(e);                                            
    }
  },

  minimizeControl: function(e) {
    this.div.style.width = "0px";
    this.div.style.height = "0px";

    this.showControls(true);

    if (e != null) {
      OpenLayers.Event.stop(e);                                            
    }
  },

  showControls: function(minimize) {
    this.maximizeDiv.style.display = minimize ? "" : "none";
    this.minimizeDiv.style.display = minimize ? "none" : "";
    this.contentDiv.style.display = minimize ? "none" : "";
  },

  loadContents: function() {
    var self = this;
    this.contentDiv = $("<div class='content'><div><a href='javascript:void(0);' id='download-kml'>Download as KML</a></div><div><a href='javascript:void(0);' id='download-fullkml'>Download as KML (old)</a></div><div><a href='javascript:void(0);' id='download-csv'>Download as CSV</a></div></div>")[0];
    $(this.contentDiv).find("#download-kml").click(function () {        
      window.open(
        MapServer.apiurl + "?" + $.param({
          format: 'appomatic_mapserver.maprenderers.MapRendererKml',
          tolerance: 'minimal',
          action: 'map',
          datetime__gte: self.map.timemin,
          datetime__lte: self.map.timemax,
          bbox: self.map.getExtent().transform(
            self.map.getProjection(),
            new OpenLayers.Projection("EPSG:4326")).toBBOX()
        })
      );
    });
    $(this.contentDiv).find("#download-fullkml").click(function () {        
      window.open(
        MapServer.exportkmlurl + "?" + $.param({
          datetime__gte: self.map.timemin,
          datetime__lte: self.map.timemax,
          bbox: self.map.getExtent().transform(
            self.map.getProjection(),
            new OpenLayers.Projection("EPSG:4326")).toBBOX()
        })
      );
    });
    $(this.contentDiv).find("#download-csv").click(function () {        
      window.open(
        MapServer.exportcsvurl + "?" + $.param({
          datetime__gte: self.map.timemin,
          datetime__lte: self.map.timemax,
          bbox: self.map.getExtent().transform(
            self.map.getProjection(),
            new OpenLayers.Projection("EPSG:4326")).toBBOX()
        })
      );
    });
    $(this.div).append(this.contentDiv);


    // maximize button div
    var img = OpenLayers.Util.getImageLocation('layer-switcher-maximize.png');
    this.maximizeDiv = OpenLayers.Util.createAlphaImageDiv(
                                "OpenLayers_Control_MaximizeDiv", 
                                null, 
                                null, 
                                img, 
                                "absolute");
    OpenLayers.Element.addClass(this.maximizeDiv, "maximizeDiv olButton");
    this.maximizeDiv.style.display = "none";

    this.div.appendChild(this.maximizeDiv);

    // minimize button div
    var img = OpenLayers.Util.getImageLocation('layer-switcher-minimize.png');
    this.minimizeDiv = OpenLayers.Util.createAlphaImageDiv(
                                "OpenLayers_Control_MinimizeDiv", 
                                null, 
                                null, 
                                img, 
                                "absolute");
    OpenLayers.Element.addClass(this.minimizeDiv, "minimizeDiv olButton");
    this.minimizeDiv.style.display = "none";

    this.div.appendChild(this.minimizeDiv);
  }
});


MapServer.Control.GeoCode = OpenLayers.Class(OpenLayers.Control, {
  CLASS_NAME: "MapServer.Control.GeoCode",
  minimizeDiv: null,
  maximizeDiv: null,
  contentDiv: null,

  initialize: function(options) {
    OpenLayers.Control.prototype.initialize.apply(this, arguments);
  },

  destroy: function() {
    this.map.events.un({buttonclick: this.onButtonClick, scope: this});
    this.events.unregister("buttonclick", this, this.onButtonClick);
    OpenLayers.Control.prototype.destroy.apply(this, arguments);
  },

  setMap: function(map) {
    OpenLayers.Control.prototype.setMap.apply(this, arguments);
    this.map.events.register("buttonclick", this, this.onButtonClick);
  },

  draw: function() {
    OpenLayers.Control.prototype.draw.apply(this);
    this.loadContents();
    this.minimizeControl();
    this.redraw();    
    return this.div;
  },

  onButtonClick: function(evt) {
    var button = evt.buttonElement;
    if (button === this.minimizeDiv) {
      this.minimizeControl();
    } else if (button === this.maximizeDiv) {
      this.maximizeControl();
    } else if (button._layerSwitcher === this.id) {
      if (button["for"]) {
        button = document.getElementById(button["for"]);
      }
      if (!button.disabled) {
        console.log(button);
      }
    }
  },


  redraw: function() {
    return this.div; 
  },

  maximizeControl: function(e) {
    this.div.style.width = "";
    this.div.style.height = "";

    this.showControls(false);

    if (e != null) {
      OpenLayers.Event.stop(e);                                            
    }
    $(this.contentDiv).find('input').focus();
  },

  minimizeControl: function(e) {
    this.div.style.width = "0px";
    this.div.style.height = "0px";

    this.showControls(true);

    if (e != null) {
      OpenLayers.Event.stop(e);                                            
    }
  },

  showControls: function(minimize) {
    this.maximizeDiv.style.display = minimize ? "" : "none";
    this.minimizeDiv.style.display = minimize ? "none" : "";
    this.contentDiv.style.display = minimize ? "none" : "";
  },

  query: function(queryString) {
    var self = this;
    OpenLayers.Request.POST({
        url: "http://www.openrouteservice.org/php/OpenLSLUS_Geocode.php",
        scope: self,
        failure: self.requestFailure,
        success: self.requestSuccess,
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        data: "FreeFormAdress=" + encodeURIComponent(queryString) + "&MaxResponse=1"
    });
  },

  requestSuccess: function(response) {
    var self = this;
    self.minimizeControl();
    var format = new OpenLayers.Format.XLS();
    var output = format.read(response.responseXML);
    if (output.responseLists[0] && output.responseLists[0].features[0]) {
      var geometry = output.responseLists[0].features[0].geometry;
      var foundPosition = new OpenLayers.LonLat(geometry.x, geometry.y).transform(
        new OpenLayers.Projection("EPSG:4326"),
        map.getProjectionObject()
      );
      self.map.setCenter(foundPosition, 16);
    } else {
      alert("Sorry, no address found");
    }
  },

  requestFailure: function(response) {
    var self = this;
    self.minimizeControl();
    alert("An error occurred while communicating with the OpenLS service. Please try again.");
  },

  loadContents: function() {
    var self = this;
    var contentDiv = $("<div class='content'>Address:</div>");
    this.contentDiv = contentDiv[0];
    $(this.div).append(this.contentDiv);

    contentDiv.mousedown(function (e) { e.stopPropagation(); });

    var input = $("<input type='text'>");
    contentDiv.append(input);

    input.keyup(function (event) {
      if (event.which == 13) {
        self.query(input.val());
        event.preventDefault();
      }
    });

    // maximize button div
    var img = OpenLayers.Util.getImageLocation('layer-switcher-maximize.png');
    this.maximizeDiv = OpenLayers.Util.createAlphaImageDiv(
                                "OpenLayers_Control_MaximizeDiv", 
                                null, 
                                null, 
                                img, 
                                "absolute");
    OpenLayers.Element.addClass(this.maximizeDiv, "maximizeDiv olButton");
    this.maximizeDiv.style.display = "none";

    this.div.appendChild(this.maximizeDiv);

    // minimize button div
    var img = OpenLayers.Util.getImageLocation('layer-switcher-minimize.png');
    this.minimizeDiv = OpenLayers.Util.createAlphaImageDiv(
                                "OpenLayers_Control_MinimizeDiv", 
                                null, 
                                null, 
                                img, 
                                "absolute");
    OpenLayers.Element.addClass(this.minimizeDiv, "minimizeDiv olButton");
    this.minimizeDiv.style.display = "none";

    this.div.appendChild(this.minimizeDiv);
  }
});


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
        new OpenLayers.Strategy.BBOX({ratio: 1}),
        this.filterStrategy
      ],
      protocol: new OpenLayers.Protocol.HTTP(
        OpenLayers.Util.extend(options.protocol, {
          url: MapServer.apiurl,
          format: new OpenLayers.Format.GeoJSON(),
          params: OpenLayers.Util.extend(options.protocol.params,
            OpenLayers.Util.extend(MapServer.getJsonFromUrl(), {
              action:'map'})),
        })),
      styleMap: new OpenLayers.StyleMap({
          "default": new OpenLayers.Style({}, {createSymbolizer: function(feature) {
              return OpenLayers.Util.extend(OpenLayers.Util.extend({}, this.defaultStyle), feature.data.style);
          }})
      }),
      renderers: ["Canvas", "SVG", "VML"]
    });
    OpenLayers.Layer.Vector.prototype.initialize.apply(this, [name, options]);
  },
  eventListeners:{
    'added': function (evt) {
       evt.map.events.register("zoomend", evt.layer, function (evt) {
         this.refresh({force:true});
       });
    },
    'featureselected': function(evt) {
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
      if (!attrs.target) attrs.target = '_blank';
      if (!attrs.description) {
        window.open(attrs.url, attrs.target);
      } else {
        var popup = new OpenLayers.Popup.FramedCloud("popup",
          new OpenLayers.LonLat(feature.geometry.bounds.right, feature.geometry.bounds.bottom),
          new OpenLayers.Size(400,300),
          attrs.description,
          null,
          true
        );
        popup.autoSize = false;
        feature.popup = popup;
        this.map.addPopup(popup);
      }
    },
    'featureunselected': function(evt){
      var feature = evt.feature;
      if (feature.popup) {
        this.map.removePopup(feature.popup);
        feature.popup.destroy();
        feature.popup = null;
      }
    },
    'loadend': function(evt) {
      this.map.events.triggerEvent('loadend', evt);
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

MapServer.Layer.KmlDir = OpenLayers.Class(OpenLayers.Layer.Vector, {
  CLASS_NAME: "MapServer.Layer.KmlDir",

  setTimeRange: function(min, max) {
    var self = this;
    $.get(
      MapServer.apiurl,
      OpenLayers.Util.extend({action: 'kmldir',
                              datetime__gte: min,
                              datetime__lte: max},
                             self.options.protocol.params),
      function(d) {
        self.protocol.datasets = d.files.map(function (filename) {
           return {url: MapServer.fileurl + filename}
        });
        self.refresh({force:true});
      },
      "json");
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


MapServer.updateUrlFromMap = function (map) {
  if (MapServer.updateUrlFromMap.noUpdate) return;
  top.window.location.hash = "#" + encodeURIComponent(JSON.stringify({
    timemin: map.timemin,
    timemax: map.timemax,
    center: map.getCenter().transform(
      map.getProjection(),
      new OpenLayers.Projection("EPSG:4326")),
    zoom: map.getZoom(),
    classes: $("body").attr("class")
  }));
}


MapServer.updateMapFromUrl = function (map) {
  MapServer.updateUrlFromMap.noUpdate = true;
  var data = JSON.parse(decodeURIComponent(top.window.location.hash.substr(1)));
  if (data.classes) {
    $("body").addClass(data.classes);
  }
  map.setCenter(
    (new OpenLayers.LonLat(data.center.lon, data.center.lat)).transform(
      new OpenLayers.Projection("EPSG:4326"),
      map.getProjection()),
    data.zoom);
  $("#time-slider").betterslider( "option", "values", [data.timemin, data.timemax]);
  map.setTimeRange(data.timemin, data.timemax);
  MapServer.updateUrlFromMap.noUpdate = false;
}


MapServer.init = function () {
  async.series([
    function(cb) {
      function mapEvent(event) {
        console.log(event);
      }

      OpenLayers.ProxyHost = MapServer.proxyurl;

      var selectFeature = new OpenLayers.Control.SelectFeature(this.vlayer);

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
          new OpenLayers.Control.KeyboardDefaults(),
          new MapServer.Control.Menu(),
          new MapServer.Control.GeoCode(),
          selectFeature
        ],
        setTimeRange: function (min, max) {
          this.timemin = min;
          this.timemax = max;
          MapServer.updateUrlFromMap(map);
          $.each(this.layers, function () {
            if (typeof this.setTimeRange != "undefined") {
              this.setTimeRange(min, max);
            }
          });
        }
      });

      map.events.register('moveend', {}, function(evt) { MapServer.updateUrlFromMap(map); });
      map.events.register('zoomend', {}, function(evt) { MapServer.updateUrlFromMap(map); });

      map.events.register('loadend', {}, function(evt) {
        var features = {};
        $.each(map.layers, function (index, layer) {
          if (layer instanceof OpenLayers.Layer.Vector) {
            $.each(layer.features, function (index, feature) {
              var date = MapServer.dateTimeToDate(MapServer.epochToDate(feature.data.datetime)).getTime() / 1000;
              if (features[date] == undefined) features[date] = [];
              features[date].push(feature);
            });
          }
        });

        $("#eventlist *").remove();
          var dates = Object.keys(features);
          dates.sort();
          $.each(dates, function (index, date) {
            var group = $("<div><h2>" + MapServer.epochToDate(date).format(MapServer.DATE_FORMAT) + "</h2></div>");
            $("#eventlist").append(group);

            features[date].sort(function(a,b){return a.data.datetime-b.data.datetime});
            $.each(features[date], function (index, feature) {
              var item = $("<div class='item'></div>");
              group.append(item);
              var link = $("<a href='javascript:void(0);'></a>");
              item.append(link);
              if (feature.data.style.externalGraphic) {
                link.append("<img src='" + feature.data.style.externalGraphic + "'>");
              }
              link.append(feature.data.title);
              link.click(function () {
                map.panTo(new OpenLayers.LonLat(feature.geometry.bounds.right, feature.geometry.bounds.bottom));
                selectFeature.select(feature);
              });
            });
          });
      });

      map.addLayer(new OpenLayers.Layer.OSM("Simple OSM Map"));

      cb();
    },

    function(cb) {
      $.get(
        MapServer.apiurl,
        OpenLayers.Util.extend(MapServer.getJsonFromUrl(), {action: 'layers'}),
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
         OpenLayers.Util.extend(MapServer.getJsonFromUrl(), {action: 'timerange'}),
         function(d) { data = d; cb(); },
         "json"
      );
    },

    function(cb) {
      $("#time-slider-label-min").html(
        MapServer.epochToDate(data.timemax-24*60*60).format(MapServer.TIME_FORMAT));
      $("#time-slider-label-max").html(
        MapServer.epochToDate(data.timemax).format(MapServer.TIME_FORMAT));

      $("#time-slider").betterslider({
        range: true,
        min: data.timemin,
        max: data.timemax,
        values: [data.timemax-24*60*60, data.timemax],
        slide: function(event, ui) {
          $("#time-slider-label-min").html(
            MapServer.epochToDate(ui.values[0]).format(MapServer.TIME_FORMAT));
          $("#time-slider-label-max").html(
            MapServer.epochToDate(ui.values[1]).format(MapServer.TIME_FORMAT));
        },
        stop: function(event, ui) {
          map.setTimeRange(ui.values[0], ui.values[1]);
        }
      });
      cb();
    },

    function(cb) {
      if (top.window.location.hash) {
        return cb();
      }
      $.get(
        MapServer.apiurl,
         OpenLayers.Util.extend(MapServer.getJsonFromUrl(), {action: 'config'}),
         function(d) {
           defaults = {
             timemin: data.timemax-24*60*60,
             timemax: data.timemax,
             center: new OpenLayers.LonLat(-118.20782, -24.9335916667),
             zoom: map.getZoom()
           }
           for (key in d) {
             defaults[key] = d[key];
           }
           if (defaults.timemin == 'start') defaults.timemin = data.timemin;
           if (defaults.timemax == 'end') defaults.timemax = data.timemax;
           top.window.location.hash = "#" + encodeURIComponent(JSON.stringify(defaults));
           cb();
         },
         "json"
      );
    },

    function(cb) {
      MapServer.updateMapFromUrl(map);

      window.onresize = function() {
        setTimeout(
          function() {
            map.updateSize();
          },
          0);
      }
      map.updateSize();

      cb();
    }

  ]);
};
