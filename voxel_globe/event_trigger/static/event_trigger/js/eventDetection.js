function EventDetectionMain() {
  this.left;
  this.right;
  this.eventIndex = 0;
  this.eventResults = [];
  this.sites = [];
  this.selectedCameraSet = -1;
  this.mapIsDisplayed = false;
  this.siteId = -1;
  this.geometryId = -1;
  this.eventIDs = null;
  var that = this;

  mapViewer = new MapViewer();
  mapViewer.setupMap({useSTKTerrain: true, geocoder: true});
  // TODO get metadata about the images and then mapViewer.setHomeLocation()
  mapViewer.viewHomeLocation();

  $(window).resize(function() {
    if (that.mapIsDisplayed) {
      that.adjustOnResize();
    }
  });

  $("#displayMap").attr('checked', false);
  $("#displayMap").click(function(e) {
    if ($(this).is(':checked')) {
      that.displayMap(e);
    } else {
      that.hideMap(e);
    }
  });

  $("#remove").click(this.remove);
  $("#back").click(function() {
    that.eventIndex -= 1;
    that.loadEventData();
  });
  $("#forward").click(function() {
    that.eventIndex += 1;
    that.loadEventData();
  });

  // request all the sattel sites from the database and put them in dropdown
  $.ajax({
    type : "GET",
    url : "/meta/rest/auto/sattelsite",
    success : function(data) {
      if (data.error) {
        alert(data.error);
        return;
      }
      var len = data.length;
      for (var i = 0; i < len; i++) {
        $("#selectSite").append('<option value="' + data[i].id + '"">' +
          data[i].name + '</option>');
      }
    }
  })

  $("#changeDetected").hide();
  $("#selectSite").on('change', function(e) {
    var siteId = this.value;
    that.selectSite(siteId);
    $("#changeDetected").show();
  });
}

EventDetectionMain.prototype.selectSite = function(siteId) {
  var that = this;
  that.eventIndex = 0;
  that.eventResults = [];

  $("select option[value='']").prop('disabled', true);
  that.siteId = siteId;
  
  $.ajax({
    type: "GET",
    url: "/meta/rest/auto/sattelsite/" + siteId,
    success: function(data) {
      that.selectedCameraSet = data.camera_set;
      that.requestEventTriggers(siteId);
    }
  })
}

EventDetectionMain.prototype.requestEventTriggers = function(siteId) {
  var that = this;
  $.ajax({
    type : "GET",
    url : "/meta/rest/auto/satteleventtrigger/?site=" + siteId,
    success : function(data) {
      if (data.error) {
        alert(data.error);
        return;
      }
      that.eventIDs = [];
      for (var i = 0; i < data.length; i++) {
        that.eventIDs = that.eventIDs.concat(data[i].event_areas);
      }
      console.log('EVENT IDS: ',that.eventIDs);      
      that.requestEventResults();
    }
  });
}

EventDetectionMain.prototype.requestEventResults = function(step=0) {

  // chain loop of ajax requests
  if (step<this.eventIDs.length) {
    var that = this;
    $.ajax({
      type : "GET",
      url : "/meta/rest/auto/satteleventresult/?geometry=" + that.eventIDs[step],
      success : function(data) {
        if (data.error) {
          alert(data.error);
          return;
        }

        for (var i = 0; i < data.length; i++) {
          that.eventResults.push(data[i]);
        }

        that.requestEventResults(++step);
      }
    });

  // complete = load mission images
  } else{
      if (this.eventResults.length == 0) {
        $("#changeDetected").html("No event results to display.")
        $("#imageDivs").hide();
        return;
      } else {
        $("#changeDetected").html('Change Detected: <span id="'  +
          'eventResultName"></span><span id="numDisplaying"></span>');
        $("#imageDivs").show();
        this.loadEventData();
      }      
  } 
}


EventDetectionMain.prototype.loadEventData = function(step=0) {
  that = this;
  var idx = that.eventIndex;

  // get mission image
  if (step==0) {
    $.ajax({
      type : "GET",
      url : "/meta/rest/auto/image",
      data : { 'id' : that.eventResults[idx].mission_image },
      success : function(data) {
        that.eventResults[idx].imgMission = data[0];
        that.loadEventData(++step);
      }
    });
  }

  // get reference image
  else if (step==1) {
    $.ajax({
      type : "GET",
      url : "/meta/rest/auto/image",
      data : { 'id' : that.eventResults[idx].reference_image },
      success : function(data) {
        that.eventResults[idx].imgReference = data[0];
        that.loadEventData(++step);
      }
    });
  }

  // get mission geometry
  else if (step==2) {
    $.ajax({
      type: "GET",
      url: "/apps/event_trigger/get_event_geometry",
      data: {
        "image_id" : that.eventResults[idx].mission_image,
        "site_id" : that.siteId,
        "sattelgeometryobject_id" : that.eventResults[idx].geometry
      },
      success: function(data) {
        that.eventResults[idx].coordsMission = zoomifyCoords(data);
        that.loadEventData(++step);   
      }
    });

  }

  // get reference geometry
  else if (step==3) {
    $.ajax({
      type: "GET",
      url: "/apps/event_trigger/get_event_geometry",
      data: {
        "image_id" : that.eventResults[idx].reference_image,
        "site_id" : that.siteId,
        "sattelgeometryobject_id" : that.eventResults[idx].geometry
      },
      success: function(data) {
        that.eventResults[idx].coordsReference = zoomifyCoords(data);
        that.loadEventData(++step);   
      }        
    });

  }

  // display
  else {
      that.display();

  }

  function zoomifyCoords(json_string) {
    var coords = JSON.parse(json_string);
    for (var i=0; i<coords.length; i++){
      coords[i][1] = -coords[i][1];
    }
    return coords;
  }

}


EventDetectionMain.prototype.display = function() {
  var that = this;

  if (that.eventIndex < 0) {
    that.eventIndex = 0;
    return;
  }
  if (that.eventIndex > that.eventResults.length - 1) {
    that.eventIndex = that.eventResults.length - 1;
    return;
  }

  var idx = that.eventIndex;

  var result = that.eventResults[idx];

  $("#significance").html(result.score);
  $("#eventResultName").html(result.name);

  $("#missionImageTitle").html(result.imgMission.name);
  $("#referenceImageTitle").html(result.imgReference.name);
  $("#numDisplaying").html('Displaying ' + (parseInt(idx) + 1) + ' of ' + that.eventResults.length);

  that.left = updateImageViewer(that.left,"leftImage",result.imgReference,result.coordsReference);
  that.right = updateImageViewer(that.right,"rightImage",result.imgMission,result.coordsMission);

  function updateImageViewer(imgViewer,divName,img,coords) {
    //if (!imgViewer || img.name != imgViewer.img.name || img.geometry != imgViewer.img.geometry) {
      $("#"+divName).html("");
      imgViewer = new ImageViewer(divName, img, that.selectedCameraSet);
      that.displayGeometry(imgViewer,coords);
    //} else {
      imgViewer.map.updateSize();
    //}
    
    return imgViewer;
  }
}

EventDetectionMain.prototype.displayGeometry = function(imgViewer, coords) {
  var drawsource = new ol.source.Vector();
  var inactiveStyle = new ol.style.Style({
    fill: new ol.style.Fill({
            color: 'rgba(255, 255, 255, 0.2)'
        }),
    stroke : new ol.style.Stroke({
      color : INACTIVE_COLOR,
      width : 5
    }),
  });

  var vector = new ol.layer.Vector({
    source : drawsource,
    style : inactiveStyle
  });

  var polygon = new ol.geom.Polygon();
  polygon.setCoordinates([coords]);

  var feature = new ol.Feature({
    name: "Polygon",
    geometry: polygon
  })

  drawsource.addFeature(feature);
  var map = imgViewer.map;
  map.addLayer(vector);
  var view = map.getView();
  view.fit(drawsource.getExtent(), map.getSize());
  
  imgViewer.map.renderSync();
}


EventDetectionMain.prototype.adjustOnResize = function() {
  if ($(window).width() > 620) {
    $("#right").width("calc(60% - 30px)");
    $("#right").css("margin-bottom", "0");
    $("#left").width("40%");
    $("#left").css("float", "left");
    $("#left").css("clear", "none");
    $("#left").css("margin-bottom", "0");
  } else {
    $("#right").width("100%");
    $("#right").css("margin-bottom", "40px");
    $("#left").width("100%");
    $("#left").css("float", "none");
    $("#left").css("clear", "both");
    $("#left").css("margin-bottom", "40px");
  }
}

EventDetectionMain.prototype.displayMap = function(e) {
  var that = this;
  that.adjustOnResize();

  $("#left").show();
  that.mapIsDisplayed = true;

  // fix ol3 canvas distortion
  that.left.map.updateSize();
  that.right.map.updateSize();
}

EventDetectionMain.prototype.hideMap = function(e) {
  var that = this;
  $("#right").width("100%");
  $("#right").css("margin-bottom", "0");
  $("#left").hide();
  that.mapIsDisplayed = false;

  // fix ol3 canvas distortion
  that.left.map.updateSize();
  that.right.map.updateSize();
}



EventDetectionMain.prototype.remove = function() {
  // TODO
  console.log('remove');
}

