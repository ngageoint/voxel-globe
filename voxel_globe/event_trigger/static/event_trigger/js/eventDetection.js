function EventDetectionMain() {
  this.results = [];
  this.images = {};
  this.left;
  this.right;
  this.i = 0;
  var that = this;

  var mapIsDisplayed = false;
  mapViewer = new MapViewer();
  mapViewer.setupMap({useSTKTerrain: true, geocoder: true});
  // TODO get metadata about the images and then mapViewer.setHomeLocation()
  mapViewer.viewHomeLocation();

  $(window).resize(function() {
    if (mapIsDisplayed) {
      adjustOnResize();
    }
  });

  var adjustOnResize = function() {
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

  var displayMap = function(e) {
    e.preventDefault();
    adjustOnResize();

    $("#left").show();
    $("#displayMap").hide();
    $("#hideMap").show();
    mapIsDisplayed = true;

    // fix ol3 canvas distortion
    that.left.map.updateSize();
    that.right.map.updateSize();
  }

  var hideMap = function(e) {
    e.preventDefault();
    $("#right").width("100%");
    $("#right").css("margin-bottom", "0");
    $("#left").hide();
    $("#displayMap").show();
    $("#hideMap").hide();
    mapIsDisplayed = false;

    // fix ol3 canvas distortion
    that.left.map.updateSize();
    that.right.map.updateSize();
  }

  // TODO just for now
  // on page load; should be on selection of event trigger
  $.ajax({
    type : "GET",
    url : "/meta/rest/auto/satteleventresult",
    success : function(data) {
      if (data.error) {
        alert(data.error);
        return;
      }

      that.results = data;
      var len = data.length;
      for (var i = 0; i < len; i++) {
        $("#selectEventResult").append('<option value="' + i + '"">' +
          that.results[i].name +
          '</option>')
      }
      i = 0;
      load_mission_image();

      function load_mission_image() {
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
            load_reference_image();
          }
        });
      }

      function load_reference_image() {
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
              display();
            }
            i++;
            if (i < len) {
              load_mission_image();
            }
          }
        });
      }
    }, dataType : 'json'
  });
  
  $("#displayMap").click(displayMap);
  $("#hideMap").click(hideMap);
  $("#back").click(function() {
    that.i -= 1;
    display();
  });
  $("#forward").click(function() {
    that.i += 1;
    display();
  });
  $("#remove").click(this.remove);

  function display() {
    var i = that.i;

    if (i < 0) {
      i = that.results.length - 1;
    }
    if (i > that.results.length - 1) {
      i = 0;
    }

    that.i = i;

    $("#leftImage").html("");
    $("#rightImage").html("");
    $("#significance").html(that.results[i].score);
    $("#eventResultName").html(that.results[i].name);
    var ref = that.images[that.results[i].id + 'reference']
    var mis = that.images[that.results[i].id + 'mission']
    $("#missionImageTitle").html(mis.name);
    $("#referenceImageTitle").html(ref.name);
    that.left = new ImageViewer("leftImage", mis);
    that.right = new ImageViewer("rightImage", ref);

    that.updateNumDisplaying(i + 1, that.results.length);
  }

  $("#selectEventResult").on('change', function(e) {
    that.i = this.value;
    display();
  })

}

EventDetectionMain.prototype.updateNumDisplaying = function(x, y) {
  $("#numDisplaying").html('Displaying ' + x + ' of ' + y);
}

EventDetectionMain.prototype.remove = function() {
  // TODO
  console.log('remove');
}

