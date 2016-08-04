function EventDetectionMain() {
  this.results = [];
  this.images = {};
  this.left;
  this.right;
  this.i = 0;
  this.sites = [];
  this.selectedCameraSet = -1;
  this.mapIsDisplayed = false;
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
    that.i -= 1;
    that.display();
  });
  $("#forward").click(function() {
    that.i += 1;
    that.display();
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
  that.results = [];
  that.i = 0;
  $("select option[value='']").prop('disabled', true);
  that.requestEventTriggers(siteId);
  $.ajax({
    type: "GET",
    url: "/meta/rest/auto/sattelsite/" + siteId,
    success: function(data) {
      that.selectedCameraSet = data[0].camera
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
      for (var i = 0; i < data.length; i++) {
        var geometries = data[i].event_areas;
        for (var j = 0; j < geometries.length; j++) {
          that.requestEventResults(geometries[j])
        }
      }
    }
  });
}

EventDetectionMain.prototype.requestEventResults = function(geometry) {
  var that = this;
  $.ajax({
    type : "GET",
    url : "/meta/rest/auto/satteleventresult/?geometry=" + geometry,
    success : function(data) {
      if (data.error) {
        alert(data.error);
        return;
      }

      for (var i = 0; i < data.length; i++) {
        that.results.push(data[i]);
      }

      var len = that.results.length;
      if (len == 0) {
        $("#changeDetected").html("No event results to display.")
        $("#imageDivs").hide();
        return;
      } else {
        $("#changeDetected").html('Change Detected: <span id="'  +
          'eventResultName"></span><span id="numDisplaying"></span>');
        $("#imageDivs").show();
      }
      
      i = 0;
      that.loadMissionImage(i, len);
    }
  })
}

EventDetectionMain.prototype.loadMissionImage = function(i, len) {
  var that = this;
  $.ajax({
    type : "GET",
    url : "/meta/rest/auto/image",
    data : { 'id' : that.results[i].mission_image },
    success : function(data) {
      var img = {
        id : data[0].id,
        name : data[0].name,
        url : data[0].zoomify_url,
        width : data[0].image_width,
        height : data[0].image_height
      }
      that.images[that.results[i].id + 'mission'] = img;
      that.loadReferenceImage(i, len);
    }
  });
}

EventDetectionMain.prototype.loadReferenceImage = function(i, len) {
  var that = this;
  $.ajax({
    type : "GET",
    url : "/meta/rest/auto/image",
    data : { 'id' : that.results[i].reference_image },
    success : function(data) {
      var img = {
        id : data[0].id,
        name : data[0].name,
        url : data[0].zoomify_url,
        width : data[0].image_width,
        height : data[0].image_height
      }
      that.images[that.results[i].id + 'reference'] = img;
      if (i == 0) {
        that.display();
      }
      i++;
      if (i < len) {
        that.loadMissionImage(i, len);
      }
    }
  });
}

EventDetectionMain.prototype.display = function() {
  var that = this;

  if (that.i < 0) {
    that.i = 0;
    return;
    // i = that.results.length - 1;
  }
  if (that.i > that.results.length - 1) {
    that.i = that.results.length - 1;
    return;
    // i = 0;
  }

  var i = that.i;

  $("#significance").html(that.results[i].score);
  $("#eventResultName").html(that.results[i].name);
  var ref = that.images[that.results[i].id + 'reference']
  var mis = that.images[that.results[i].id + 'mission']
  $("#missionImageTitle").html(mis.name);
  $("#referenceImageTitle").html(ref.name);
  that.left = updateImageViewer(that.left,"leftImage",ref);
  that.right = updateImageViewer(that.right,"rightImage",mis);
  that.updateNumDisplaying((parseInt(i) + 1), that.results.length);

  function updateImageViewer(imgViewer,divName,img) {
      if (!imgViewer || img.name != imgViewer.img.name) {
        $("#"+divName).html("");
        imgViewer = new ImageViewer(divName, img, that.selectedCameraSet);
      } else {
        imgViewer.map.updateSize();
      }
      return imgViewer;
  }
}

EventDetectionMain.prototype.updateNumDisplaying = function(x, y) {
  $("#numDisplaying").html('Displaying ' + x + ' of ' + y);
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

