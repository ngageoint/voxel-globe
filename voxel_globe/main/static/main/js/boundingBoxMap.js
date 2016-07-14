
/* 
 * Functionality for creating and editing a semitransparent white bounding cube,
 * for use by the build_voxel_world and create_site apps. As it is currently,
 * these functions rely on certain conventions in form element ids, for example
 * id_north_d means the form element holding the value for the northernmost
 * latitude of the cube, in degrees. Other ids follow this same pattern.
 */

// given a values object which contains nesw and top/bottom values (in degrees
// and meters, respectively), create and display the bounding box
MapViewer.prototype.createBoundingBox = function(values) {
  this.values = values;
  this.prevValues = $.extend({}, values);

  // make sure the values passed in are valid
  // (should always be valid, else developer error)
  var v = this.validateBoundingBox(values, false);
  if (v !== "valid") {
    alert(v);
    return;
  }

  var viewer = this.cesiummap;
  var entities = viewer.entities;

  // if bounding box already exists, remove before creating a new one
  if (this.boundingBox) {
    entities.remove(this.boundingBox);
  }

  var that = this;

  // add the bounding box entity
  this.boundingBox = entities.add({
    rectangle : {
      coordinates : new Cesium.CallbackProperty(function(time, result) {
        return new Cesium.Rectangle.fromDegrees(
          that.values.west, 
          that.values.south, 
          that.values.east, 
          that.values.north
        );
      }, false),
      extrudedHeight : new Cesium.CallbackProperty(function(time, result) {
        return that.values.top;
      }, false),
      height: new Cesium.CallbackProperty(function(time, result) {
        return that.values.bottom;
      }, false),
      outline : true,
      outlineColor : Cesium.Color.WHITE,
      outlineWidth : 3,
      material : Cesium.Color.WHITE.withAlpha(0.2),
    },
    name : "Bounding Box"
  });

  this.boundingBox.description = "The bounding box specified here will determine " +
  "the boundaries of the scene containing all the voxels. An initial box was " +
  "pre-calculated during SFM processing to include most of the tie points " + 
  "while excluding outliers, but you can now change any of the values or " +
  "click and drag the image to update the bounding box estimates."

  // zoom to the bounding box and once it's there, set the map to visible
  document.getElementById('right').style.display = 'block';
  document.getElementById('right').style.visibility = 'hidden';
  this.setHomeEntity(this.boundingBox);
  this.setBoundingBoxEditable();
}

MapViewer.prototype.destroyBoundingBox = function() {
  if (this.boundingBox) {
    this.corners.removeAll();
    this.cesiummap.entities.removeAll();
    this.values = {};
  }
}

// given a form update event evt, update the bounding box appropriately
MapViewer.prototype.updateBoundingBox = function(evt) {
  var target = evt.currentTarget.id;
  var edgeName = target.substring(3, target.length - 2);
  this.updateEdge(edgeName);
  this.viewHomeLocation();
  this.prevValues = $.extend({}, this.values);
  this.updateCorners();
}

// update all edges at once when no form change has been detected, which
// happens on the error condition when north becomes greater than south and the
// two values have to switch
MapViewer.prototype.updateAllEdges = function(values) {
  this.destroyBoundingBox();
  this.createBoundingBox(values);
  document.getElementById('right').style.visibility = 'visible';
}

MapViewer.prototype.updateEdge = function(edgeName) {
  var edge = document.getElementById("id_" + edgeName + "_d").value;
  var tempValues = $.extend({}, this.values);
  tempValues[edgeName] = parseFloat(edge);

  var v = this.validateBoundingBox(tempValues, false);
  if (v !== "valid") {
    alert(v);
    document.getElementById("id_" + edgeName + "_d").value = this.values[edgeName];
    if (document.getElementById("id_" + edgeName + "_m")) {
      update_bbox_meter();
    }
    return;
  } else {
    this.values = tempValues;
  }
}

// given a values object holding nesw and top/bottom values, check that these
// values form a valid bounding box. if so, return 'valid'; otherwise return
// an informative error message.
MapViewer.prototype.validateBoundingBox = function(values, nope) {
  var north = values.north; var south = values.south;
  var west = values.west; var east = values.east;
  var top = values.top; var bottom = values.bottom;

  if (north < -90 || north > 90) {
    return "North latitude must be between -90 and 90 degrees.";
  }

  if (south < -90 || south > 90) {
    return "South latitude must be between -90 and 90 degrees.";
  }

  if (north == south) {
    return "North and south latitude must not be equal."
  }

  if (east < -180 || east > 180) {
    return "East longitude must be between -180 and 180 degrees.";
  }

  if (west < -180 || west > 180) {
    return "West longitude must be between -180 and 180 degrees.";
  }

  if (top == bottom) {
    return "Top and bottom altitudes must not be equal."
  }

  if (east == west) {
    return "East and west longitude must not be equal.";
  }

  if (top < bottom) {
    return "Top altitude must be greater than bottom altitude.";
  }

  if (north < south) {
    return "North latitude must be greater than south latitude.";
  }
  
  if (nope) {
    return "nope";
  }
  
  return "valid";
}

/* 
 * Functionality for making the cube editable within the cesium map view.
 * Attaches draggable icons to each of its corners that can be
 * moved to adjust the bounding latitude and longitude of the box, and draggable
 * height handles for both top and bottom.
 */
MapViewer.prototype.setBoundingBoxEditable = function() {
  // find its coordinates, top and bottom
  var coords = this.boundingBox.rectangle.coordinates.getValue();
  var top = this.boundingBox.rectangle.extrudedHeight.getValue();
  var bot = this.boundingBox.rectangle.height.getValue();

  // add billboards for each of its eight corners and up/down handles to the map
  if (this.corners) {
    this.corners.removeAll();
  } else {
    this.corners = new Cesium.BillboardCollection();
  }

  var viewer = this.cesiummap;
  var corners = this.corners;


  if (coords.east > coords.west) {
    var topBottomLongitude = (coords.east - coords.west) / 2 + coords.west;
  } else {
    var topBottomLongitude = (coords.east - coords.west + Cesium.Math.TWO_PI) 
      / 2 + coords.west;;
  }

  new Handle(coords.west, coords.south, top, corners, "swt", this);
  new Handle(coords.west, coords.north, top, corners, "nwt", this);
  new Handle(coords.west, coords.south, bot, corners, "swb", this);
  new Handle(coords.west, coords.north, bot, corners, "nwb", this);
  new Handle(coords.east, coords.south, top, corners, "set", this);
  new Handle(coords.east, coords.north, top, corners, "net", this);
  new Handle(coords.east, coords.south, bot, corners, "seb", this);
  new Handle(coords.east, coords.north, bot, corners, "neb", this);
  new Handle(topBottomLongitude, coords.south, top, corners, "top", this);
  new Handle(topBottomLongitude, coords.south, bot, corners, "bottom", this);
  viewer.scene.primitives.add(corners);

  var that = this;
  // set up handlers that listen for clicks on the buttons
  var handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);

  handler.setInputAction(
    function(click) {
      var i;
      var pickedObject;

      // use drillPick so we can select even corners that are behind the box
      var pickedPrimitives = viewer.scene.drillPick(click.position);
      var length = pickedPrimitives.length;

      for (i = 0; i < length; i++) {
        pickedObject = pickedPrimitives[i];
        if (Cesium.defined(pickedObject) && 
            ((pickedObject.id[0] instanceof Handle))) {
          // if an instance of Corner or Handle, call that object's onClick()
          that.moveHandles(click.position, pickedObject.id[0]);
          return;
        }
      }
    }, Cesium.ScreenSpaceEventType.LEFT_DOWN
  );
}

MapViewer.prototype.moveHandles = function(position, handle) {
  var that = this;
  this.enableRotation(false);
  var plane = handle.findIntersectingPlane();
  this.prevValues = $.extend({}, this.values);
  var anchor = getAnchorPoint(handle.name);

  function onDrag(position) {
    var pickRay = that.cesiummap.scene.camera.getPickRay(position);
    // find the intersection of the plane and the pickRay; this is the new pos
    var newPosition = Cesium.Ellipsoid.WGS84.cartesianToCartographic(
          Cesium.IntersectionTests.rayPlane(pickRay, plane));
    var newPos = {
      'longitude': Cesium.Math.toDegrees(newPosition.longitude),
      'latitude': Cesium.Math.toDegrees(newPosition.latitude),
      'height': newPosition.height
    }

    if (handle.name == 'top' || handle.name == 'bottom') {
      that.values.bottom = Math.min(newPos.height, anchor.height);
      that.values.top = Math.max(newPos.height, anchor.height);
    } else {
      that.values.south = Math.min(newPos.latitude, anchor.latitude);
      that.values.north = Math.max(newPos.latitude, anchor.latitude);
      that.values.east = Math.max(newPos.longitude, anchor.longitude);
      that.values.west = Math.min(newPos.longitude, anchor.longitude);
    }

    // if international date line, switch e & w. otherwise, as normal.
    if (that.values.east > 0 && that.values.west < 0 && 
        ((that.values.east - that.values.west) > Cesium.Math.PI)) {
      var temp = that.values.east;
      that.values.east = that.values.west;
      that.values.west = temp;
    }

    var v = that.validateBoundingBox(that.values);
    if (v !== "valid") {  //TODO test this
      // if an error string is returned, alert the user, then
      // recover from the error by restoring the previous values
      alert(v);
      that.values = that.prevValues;
      that.updateCorners();
      onDragEnd();
    }

    updateFormFields(that.values);
    that.updateCorners();
  }

  function onDragEnd() {
    handler.destroy();
    that.enableRotation(true);
  }

  var handler = new Cesium.ScreenSpaceEventHandler(this.cesiummap.scene.canvas);

  handler.setInputAction(function(movement) {
    onDrag(movement.endPosition);
  }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);

  handler.setInputAction(function(movement) {
    onDragEnd();
  }, Cesium.ScreenSpaceEventType.LEFT_UP);

  function getAnchorPoint(id) {
    var values = that.values;
    var lat; var lon;
    if (id[0] == 's') {
      lat = values.north;
    } else if (id[0] == 'n') {
      lat = values.south;
    }
    if (id[1] == 'w') {
      lon = values.east;
    } else if (id[1] == 'e') {
      lon = values.west;
    }
    if (id == 'top') {
      height = values.bottom;
    } else if (id == 'bottom') {
      height = values.top;
    } else {
      height = 0;
    }
    return {'longitude': lon, 'latitude': lat, 'height': height}
  }

}

MapViewer.prototype.enableRotation = function(enable) {
  this.cesiummap.scene.screenSpaceCameraController.enableRotate = enable;
}

/*
 * Once one corner or handle has been changed, update the rest as well to 
 * reflect the new positions of the bounding box.
 */
MapViewer.prototype.updateCorners = function() {
  var coords = this.boundingBox.rectangle.coordinates.getValue();
  var top = this.boundingBox.rectangle.extrudedHeight.getValue();
  var bot = this.boundingBox.rectangle.height.getValue();

  // using a scratch variable is faster here than constantly defining a new
  var scratchPosition = new Cesium.Cartesian3;
  var ellipsoid = this.cesiummap.scene.mapProjection.ellipsoid;
  var corners = this.corners;
  var len = corners.length;

  if (coords.east > coords.west) {
    var topBottomLongitude = (coords.east - coords.west) / 2 + coords.west;
  } else {
    var topBottomLongitude = (coords.east - coords.west + Cesium.Math.TWO_PI) 
      / 2 + coords.west;
  }

  for (var i = 0; i < len; i++) {
    var bill = corners.get(i);
    var name = bill.id[1];
    switch(name) {
      case 'swt':
        bill.position = Cesium.Cartesian3.fromRadians(coords.west, coords.south,
          top, ellipsoid, scratchPosition);
        break;
      case 'nwt':
        bill.position = Cesium.Cartesian3.fromRadians(coords.west, coords.north, 
          top, ellipsoid, scratchPosition);
        break;
      case 'swb':
        bill.position = Cesium.Cartesian3.fromRadians(coords.west, coords.south,
          bot, ellipsoid, scratchPosition);
        break;
      case 'nwb':
        bill.position = Cesium.Cartesian3.fromRadians(coords.west, coords.north,
          bot, ellipsoid, scratchPosition);
        break;
      case 'set':
        bill.position = Cesium.Cartesian3.fromRadians(coords.east, coords.south,
          top, ellipsoid, scratchPosition);
        break;
      case 'net':
        bill.position = Cesium.Cartesian3.fromRadians(coords.east, coords.north,
          top, ellipsoid, scratchPosition);
        break;
      case 'seb':
        bill.position = Cesium.Cartesian3.fromRadians(coords.east, coords.south,
          bot, ellipsoid, scratchPosition);
        break;
      case 'neb':
        bill.position = Cesium.Cartesian3.fromRadians(coords.east, coords.north,
          bot, ellipsoid, scratchPosition);
        break;
      case 'top':
        bill.position = Cesium.Cartesian3.fromRadians(
          topBottomLongitude, coords.south, top);
        break;
      case 'bottom':
        bill.position = Cesium.Cartesian3.fromRadians(
          topBottomLongitude, coords.south, bot);
        break;
    }
  }
}
