// Given an ol3 map, a position string (e.g. "topright", etc.), and optionally
// upRotation and northRotation which are angles in radians, create the rotation
// control panel on the map's canvas. The rotation control panel includes a
// round rotation slider, and one to three buttons to reset the rotation to some
// known angle -- imageUp, upIsUp (buildings), and northIsUp.
function RotationControlPanel(map, position, upRotation, northRotation) {
  this.map = map;
  this.setupDiv(position);

  // all images have a rotation slider as well as the default ol3 imageUp button
  this.addRotationSlider();
  this.addImageUp();

  // but images only get an upIsUp and northIsUp button if up and north angles 
  // are defined
  if (upRotation) {
    this.addUpIsUp(upRotation);
  }
  if (northRotation) {
    this.addNorthIsUp(northRotation);
  }
}

// Set up the div the controls will live inside. Options for position are
// "topleft", "topright", "bottomleft", "bottomright".
RotationControlPanel.prototype.setupDiv = function(position) {
  var that = this;

  if (typeof that.map.getTarget() == 'string') {
    var $target = $("#" + that.map.getTarget());
  } else {
    var $target = $(target);
  }

  $target.find(".ol-overlaycontainer-stopevent")
         .html("")
         .append('<div class="rotation-controls"></div>');
  $target = $target.find(".rotation-controls");

  var offset = "0.2em"

  switch(position) {
    case "bottomright":
      $target.css("bottom", offset);
      $target.css("right", offset);
      break;
    case "topright":
      $target.css("top", offset);
      $target.css("right", offset);
      break;
    case "bottomleft":
      $target.css("bottom", offset);
      $target.css("left", offset);
      break;
    case "topleft":
      $target.css("top", offset);
      $target.css("left", offset);
      break;
    default:
      $target.css("top", offset);
      $target.css("right", offset);
      break;
  }

  that.target = $target[0];
}

// Adds the image up button, which is just the ol3 default except that it
// doesn't autohide when the angle is already 0.
RotationControlPanel.prototype.addImageUp = function() {
  var that = this;
  var imageUp = new ol.control.Rotate({
    'autoHide': false,
    'target': that.target
  });
  that.map.addControl(imageUp);
  $(imageUp.element).addClass("imageUp");
  $(imageUp.element).append('<div class="rotation-title">Image up</div>');
  $(imageUp.element).find(".ol-rotate-reset").removeAttr("title");
}

// Add upIsUp button, overriding the resetNorth and render functions so that
// instead of returning us to 0 with respect to the image, it returns us to
// whatever the upIsUp angle for this image and camera are defined to be
RotationControlPanel.prototype.addUpIsUp = function(angle) {
  var that = this;
  var upIsUp = new ol.control.Rotate({
    'autoHide': false,
    'tipLabel': 'Up is up',
    'resetNorth': that.getRotationFunction(angle),
    'render': that.getRenderFunction("upIsUp", angle),
    'target': that.target
  });
  that.map.addControl(upIsUp);
  $(upIsUp.element).addClass("upIsUp");
  $(upIsUp.element).append('<div class="rotation-title">Up is up</div>');
  $(upIsUp.element).find(".ol-rotate-reset").removeAttr("title");
}

// Same as above but for northIsUp angle
RotationControlPanel.prototype.addNorthIsUp = function(angle) {
  var that = this;
  var northIsUp = new ol.control.Rotate({
    'autoHide': false,
    'tipLabel': 'North is up',
    'resetNorth': that.getRotationFunction(angle),
    'render': that.getRenderFunction("northIsUp", angle),
    'target': that.target
  });
  that.map.addControl(northIsUp)
  $(northIsUp.element).addClass("northIsUp");
  $(northIsUp.element).append('<div class="rotation-title">North is up</div>');
  $(northIsUp.element).find(".ol-rotate-reset").removeAttr("title");
}

// Adds the Google-Earth-esque rotation slider control, which allows users
// to drag a little circle around a bigger circle to determine image angle.
RotationControlPanel.prototype.addRotationSlider = function() {
  var that = this;
  var $target = $(that.target);
  $target.append('<div class="rotation-slider-background ol-control">' + 
                    '<div class="rotation-slider-outer">' + 
                      '<div class="rotation-slider-rectangle">' +
                        '<div class="rotation-slider-inner"' +
                  '</div></div></div></div>');

  // background is just the background area, for visual appeal
  // outer is the donut shape
  var $outer = $target.find(".rotation-slider-outer");
  // rectangle is invisible, but it's the div that's actually rotating when
  // we call the rotate function. this is necessary to allow the slider to
  // rotate with respect to the outer div, rather than simply around itself
  var $rectangle = $target.find(".rotation-slider-rectangle");
  // and inner is the small circle that the user drags around
  var $inner = $target.find(".rotation-slider-inner");

  // listen for click and drag events on the inner div
  var clicked = false;

  $inner.mousedown(function() {
    clicked = true;
    $("body").css("cursor", "pointer");
    enableSelect(false);
  });

  // listen for mousemove and mouseup on the entire document when clicked,
  // because the users' cursors will probably 'drift' away from the actual
  // target as they're dragging
  $(document).mousemove(function(event) {
    if (clicked) {
      event.preventDefault();
      // find the center of the outer donut-shaped div
      // we have to recompute this every time in case the page resizes
      var offset = $outer.offset();
      var width = $outer.outerWidth();
      var height = $outer.outerHeight();
      var centerX = offset.left + width / 2;
      var centerY = offset.top + height / 2;
      var x = event.clientX;
      var y = event.clientY;

      // find angle in radians between (x, y) and (centerX, centerY)
      var angle = - Math.atan2(centerX - x, centerY - y);
      rotate(angle);
      that.map.getView().setRotation(angle);
    }
  });

  $(document).mouseup(function() {
    clicked = false;
    $("body").css("cursor", "auto");
    enableSelect(true);
  });

  // rotate the slider control
  function rotate(radians) {
    var transform = "rotate(" + radians + "rad)";
    $rectangle.css({
      "-ms-transform": transform,
      "-webkit-transform": transform,
      "transform": transform
    });
  }

  // disables or enables select on the entire document - when users are clicking
  // and dragging the slider around, they don't want to be bothered by text
  // also selecting
  function enableSelect(enable) {
    if (enable) {
      $("body").css({
        "-webkit-touch-callout":"auto",
        "-webkit-user-select":"auto",
        "-khtml-user-select":"auto",
        "-moz-user-select":"auto",
        "user-select":"auto"
      });
    } else {
      $("body").css({
        "-webkit-touch-callout":"none",
        "-webkit-user-select":"none",
        "-khtml-user-select":"none",
        "-moz-user-select":"none",
        "user-select":"none"
      });
    }
  }

  // if the user rotates the map without using the rotation slider (e.g. with
  // one of the three buttons, or with alt+shift+drag), then we need to update
  // the rotation slider's position to reflect the current state of things
  that.map.on('postrender', function(mapEvent) {
    var frameState = mapEvent.frameState;
    if (!frameState) {
      return;
    }
    var rotation = frameState.viewState.rotation;
    rotate(rotation);
  });

  var $background = $target.find(".rotation-slider-background");
  $background.append('<div class="rotation-title">Rotate</div>');
}

// Returns a function (because javascript is crazy) that'll rotate the map
// to the given angle. basically just lifted from the ol3 source with the
// modification that we are rotating to the given angle and not 0.
// use this function to override the default behavior for ol3's rotateNorth.
RotationControlPanel.prototype.getRotationFunction = function(angle) {
  var that = this;
  angle = angle % (2 * Math.PI);
  var f = function() {
    var view = that.map.getView();
    if (!view) {
      return;
    }
    var currentRotation = view.getRotation();
    if (currentRotation !== undefined) {
      currentRotation = currentRotation % (2 * Math.PI);
      if (currentRotation < angle + -Math.PI) {
        currentRotation += 2 * Math.PI;
      }
      if (currentRotation > angle + Math.PI) {
        currentRotation -= 2 * Math.PI;
      }
      that.map.beforeRender(ol.animation.rotate({
        rotation: currentRotation,
        duration: 250,
        easing: ol.easing.easeOut
      }));
      view.setRotation(angle);
    }
  }
  return f;
}

// Returns a function that gets called every time the control is rendered,
// so it's responsible for rotating the arrow icon around to correspond to the
// current rotation of the image. use this function to override the default
// behavior for ol3 controls' render function, which will just have them all
// point to imageUp.
RotationControlPanel.prototype.getRenderFunction = function(className, angle) {
  var that = this;
  var $target = $(that.target);
  
  angle = angle % (2 * Math.PI);
  var f = function(mapEvent) {
    var $label = $target.find("." + className).find(".ol-compass");
    var frameState = mapEvent.frameState;
    if (!frameState) {
      return;
    }
    var rotation = frameState.viewState.rotation;
    var transform = 'rotate(' + (rotation - angle) + 'rad)';
    $label.css({
      "-ms-transform" : transform,
      "-webkit-transform" : transform,
      "transform" : transform
    })
  }
  return f;
}