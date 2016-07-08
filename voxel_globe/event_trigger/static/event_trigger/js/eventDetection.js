function EventDetectionMain() {
  this.images = [];
  this.left;
  this.right;
  this.i = 0;
  var that = this;

  mapViewer = new MapViewer();
  mapViewer.setupMap({useSTKTerrain: true, geocoder: true});
  // TODO get metadata about the images and then mapViewer.setHomeLocation()
  mapViewer.viewHomeLocation();

  $(window).resize(function() {
    if (mapIsDisplayed) {
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
  });

  var mapIsDisplayed = false;

  var displayMap = function(e) {
    e.preventDefault();
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
  $.ajax({
    type : "GET",
    url : "/meta/rest/auto/image",
    data : {
      imageset: 5
    },
    success : function(data) {
      if (data.error) {
        alert(data.error);
        return;
      }

      for (var i = 0; i < data.length; i++) {
        var img = {
          id : data[i].id,
          name : data[i].name,
          url : data[i].zoomify_url,
          width : data[i].image_width,
          height : data[i].image_height
        };
        that.images.push(img);
      }

      display();

    }, dataType : 'json'
  });
  
  var back = this.back;

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
      i = that.images.length - 1;
    }
    if (i > that.images.length - 1) {
      i = 0;
    }

    that.i = i;

    var j = i + 1;

    if (j < 0) {
      j = that.images.length - 1;
    }
    if (j > that.images.length - 1) {
      j = 0;
    }

    $("#leftImage").html("");
    $("#rightImage").html("");
    that.left = new ImageViewer("leftImage", that.images[i]);
    that.right = new ImageViewer("rightImage", that.images[j]);

    that.updateNumDisplaying(i + 1, that.images.length);
  }
}

EventDetectionMain.prototype.updateNumDisplaying = function(x, y) {
  $("#numDisplaying").html('Displaying ' + x + ' of ' + y);
}

EventDetectionMain.prototype.remove = function() {
  // TODO
  console.log('remove');
}

