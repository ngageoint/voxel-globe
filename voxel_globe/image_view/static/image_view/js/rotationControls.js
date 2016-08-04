function RotationControlPanel(map, position, imageId) {
  this.map = map;
  this.rotationControls = {};  // TODO for rotation of little icon dude
  this.getImageAngles(imageId);
  this.setupDiv(position);
  this.addRotationSlider();
  this.addImageUp();
  this.addUpIsUp(Math.PI / 2);
  this.addNorthIsUp(-Math.PI / 3);
}

RotationControlPanel.prototype.getImageAngles = function(imageId) {
  // TODO
  console.log(imageId);
}

RotationControlPanel.prototype.setupDiv = function(position) {
  var that = this;

  if (typeof that.map.getTarget() == 'string') {
    var $target = $("#" + that.map.getTarget());
  } else {
    var $target = $(target);
  }

  $target.find(".ol-overlaycontainer-stopevent")
      .append('<div id="rotation-controls"></div>')
  $target = $("#rotation-controls");

  var offset = "0.2em"

  switch(position) {
    case "bottomright":
      $target.css("bottom",offset);
      $target.css("right",offset);
      break;
    case "topright":
      $target.css("top",offset);
      $target.css("right",offset);
      break;
    case "bottomleft":
      $target.css("bottom",offset);
      $target.css("left",offset);
      break;
    case "topleft":
      $target.css("top",offset);
      $target.css("left",offset);
      break;
    default:
      $target.css("top",offset);
      $target.css("right",offset);
      break;
  }

  that.target = $target[0];
}

RotationControlPanel.prototype.addImageUp = function() {
  var that = this;
  var imageUp = new ol.control.Rotate({
    'autoHide': false,
    'tipLabel': 'Image up',
    'target': that.target
  });
  that.map.addControl(imageUp);
}

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
  $(upIsUp.element).attr("id", "upIsUp");
}

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
  $(northIsUp.element).attr("id", "northIsUp");
}

RotationControlPanel.prototype.addRotationSlider = function() {
  var that = this;
  var $target = $(that.target);
  $target.append('<div class="rotation-slider-background ol-control">' + 
                    '<div class="rotation-slider-outer">' + 
                      '<div class="rotation-slider-rectangle">' +
                        '<div class="rotation-slider-inner"' +
                  '</div></div></div></div>');

  var $outer = $target.find(".rotation-slider-outer");
  var $rectangle = $target.find(".rotation-slider-rectangle");
  var $inner = $target.find(".rotation-slider-inner");

  // find the center of the outer div
  var offset = $outer.offset();
  var width = $outer.outerWidth();
  var height = $outer.outerHeight();
  var centerX = offset.left + width / 2;
  var centerY = offset.top + height / 2;

  // listen for click and drag events
  var clicked = false;

  $inner.mousedown(function() {
    clicked = true;
    $("body").css("cursor", "pointer");
  });
  $(document).mousemove(function(event) {
    if (clicked) {
      var x = event.clientX;
      var y = event.clientY;
      // find angle in radians between (x, y) and (centerX, centerY)
      r = - Math.atan2(centerX - x, centerY - y);
      rotate(r);
      that.map.getView().setRotation(r);
    }
  });
  $(document).mouseup(function() {
    clicked = false;
    $("body").css("cursor", "auto");
  });

  // rotate the slider control and rotate the map accordingly
  function rotate(radians) {
    var transform = "rotate(" + radians + "rad)";
    $rectangle.css({
      "-ms-transform": transform,
      "-webkit-transform": transform,
      "transform": transform
    });
  }

  that.map.on('postrender', function(mapEvent) {
    var frameState = mapEvent.frameState;
    if (!frameState) {
      return;
    }
    var rotation = frameState.viewState.rotation;  // TODO
    rotate(rotation);
  });
}

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

RotationControlPanel.prototype.getRenderFunction = function(id, angle) {
  angle = angle % (2 * Math.PI);
  var f = function(mapEvent) {
    var $label = $("#" + id).find(".ol-compass");
    var frameState = mapEvent.frameState;
    if (!frameState) {
      return;
    }
    var rotation = frameState.viewState.rotation;  // TODO
    var transform = 'rotate(' + (rotation + angle) + 'rad)';
    $label.css({
      "-ms-transform" : transform,
      "-webkit-transform" : transform,
      "transform" : transform
    })
  }
  return f;
}