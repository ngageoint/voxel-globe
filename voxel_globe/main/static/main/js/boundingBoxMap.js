
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
  var v = this.validateBoundingBox(values);
  if (v !== "valid") {
    alert(v);
    return;
  }

  var viewer = this.cesiummap;
  var entities = viewer.entities;
  var coords = new Cesium.Rectangle.fromDegrees(
    values.west, values.south, values.east, values.north);

  //if bounding box already exists, remove before creating a new one
  if (this.boundingBox) {
    entities.remove(this.boundingBox);
  }

  // add the bounding box entity
  this.boundingBox = entities.add({
    rectangle : {
      coordinates : Cesium.Rectangle.fromDegrees(
        values.west, 
        values.south, 
        values.east, 
        values.north),
      extrudedHeight : values.top,
      height: values.bottom,
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
  this.viewHomeLocation();
  this.setBoundingBoxEditable();
}

MapViewer.prototype.destroyBoundingBox = function() {
  if (this.boundingBox) {
    this.corners.removeAll();
    this.cesiummap.entities.removeAll();
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

MapViewer.prototype.updateEdge = function(edgeName) {
  var edge = document.getElementById("id_" + edgeName + "_d").value;
  this.values[edgeName] = parseFloat(edge);

  var v = this.validateBoundingBox(this.values);
  if (v !== "valid") {
    alert(v);
    this.values = this.prevValues;
    document.getElementById("id_" + edgeName + "_d").value = this.values[edgeName];
    update_bbox_meter();
    return;
  }

  switch(edgeName) {
    case "bottom":
      this.boundingBox.rectangle.height = edge;
      break;
    case "top":
      this.boundingBox.rectangle.extrudedHeight = edge;
      break;
    default:
      var coords = this.boundingBox.rectangle.coordinates.getValue();
      coords[edgeName] = Cesium.Math.toRadians(edge);
      this.boundingBox.rectangle.coordinates = coords;
  }
}

// given a values object holding nesw and top/bottom values, check that these
// values form a valid bounding box. if so, return 'valid'; otherwise return
// an informative error message.
MapViewer.prototype.validateBoundingBox = function(values) {
  var north = values.north; var south = values.south;
  var west = values.west; var east = values.east;
  var top = values.top; var bottom = values.bottom;

  // if (!north || !south || !west || !east || !top || !bottom) {
  //   return "Please make sure all values are filled in.";
  // }

  if (top < bottom) {
    return "Top altitude must be greater than bottom altitude.";
  }

  if (top == bottom) {
    return "Top and bottom altitudes are equal, which means your " +
    "bounding box isn't three dimensional."
  }

  if (north < -90 || north > 90) {
    return "North latitude must be between -90 and 90 degrees.";
  }

  if (south < -90 || south > 90) {
    return "South latitude must be between -90 and 90 degrees.";
  }

  if (north < south) {
    return "North latitude must be greater than south latitude.";
  }

  if (north == south) {
    return "North and south latitude are equal, which means your " +
    "bounding box isn't three dimensional."
  }

  if (east < -180 || east > 180) {
    return "East longitude must be between -180 and 180 degrees.";
  }

  if (west < -180 || west > 180) {
    return "West longitude must be between -180 and 180 degrees.";
  }

  if (east == west) {
    return "East and west longitude are equal, which means your " +
    "bounding box isn't three dimensional."
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

  new Handle(coords.west, coords.south, top, corners, "swt", this);
  new Handle(coords.west, coords.north, top, corners, "nwt", this);
  new Handle(coords.west, coords.south, bot, corners, "swb", this);
  new Handle(coords.west, coords.north, bot, corners, "nwb", this);
  new Handle(coords.east, coords.south, top, corners, "set", this);
  new Handle(coords.east, coords.north, top, corners, "net", this);
  new Handle(coords.east, coords.south, bot, corners, "seb", this);
  new Handle(coords.east, coords.north, bot, corners, "neb", this);
  new Handle(((coords.east - coords.west) / 2) + coords.west, coords.south, top,
    corners, "top", this);
  new Handle(((coords.east - coords.west) / 2) + coords.west, coords.south, bot,
    corners, "bottom", this);
  viewer.scene.primitives.add(corners);

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
          pickedObject.id[0].onClick(click.position);
          return;
        }
      }
    }, Cesium.ScreenSpaceEventType.LEFT_DOWN
  );
}

/*
 * Given a new cartesian position and the name of the corner that has just been
 * moved (e.g. 'swt' for southwest top, etc.), update the white bounding box
 * visually on the screen, and also update the global values array.
 */
MapViewer.prototype.drawUpdateBoundingBox = function(cartesian, name) {
  var cartographic = Cesium.Ellipsoid.WGS84.cartesianToCartographic(cartesian);
  var coords = this.boundingBox.rectangle.coordinates.getValue();

  switch(name) {
    case 'swt':
      this.values.west = Cesium.Math.toDegrees(cartographic.longitude);
      this.values.south = Cesium.Math.toDegrees(cartographic.latitude);
      coords.west = cartographic.longitude;
      coords.south = cartographic.latitude;
      break;
    case 'nwt':
      this.values.north = Cesium.Math.toDegrees(cartographic.latitude);
      this.values.west = Cesium.Math.toDegrees(cartographic.longitude);
      coords.north = cartographic.latitude;
      coords.west = cartographic.longitude;
      break;
    case 'swb':
      this.values.south = Cesium.Math.toDegrees(cartographic.latitude);
      this.values.west = Cesium.Math.toDegrees(cartographic.longitude);
      coords.south = cartographic.latitude;
      coords.west = cartographic.longitude;
      break;
    case 'nwb':
      this.values.north = Cesium.Math.toDegrees(cartographic.latitude);
      this.values.west = Cesium.Math.toDegrees(cartographic.longitude);
      coords.north = cartographic.latitude;
      coords.west = cartographic.longitude;
      break;
    case 'set':
      this.values.south = Cesium.Math.toDegrees(cartographic.latitude);
      this.values.east = Cesium.Math.toDegrees(cartographic.longitude);
      coords.south = cartographic.latitude;
      coords.east = cartographic.longitude;
      break;
    case 'net':
      this.values.north = Cesium.Math.toDegrees(cartographic.latitude);
      this.values.east = Cesium.Math.toDegrees(cartographic.longitude);
      coords.north = cartographic.latitude;
      coords.east = cartographic.longitude;
      break;
    case 'seb':
      this.values.south = Cesium.Math.toDegrees(cartographic.latitude);
      this.values.east = Cesium.Math.toDegrees(cartographic.longitude);
      coords.south = cartographic.latitude;
      coords.east = cartographic.longitude;
      break;
    case 'neb':
      this.values.north = Cesium.Math.toDegrees(cartographic.latitude);
      this.values.east = Cesium.Math.toDegrees(cartographic.longitude);
      coords.north = cartographic.latitude;
      coords.east = cartographic.longitude;
      break;
    case 'top':
      this.boundingBox.rectangle.extrudedHeight = cartographic.height;
      this.values.top = cartographic.height;
      return;
    case 'bottom':
      this.boundingBox.rectangle.height = cartographic.height;
      this.values.bottom = cartographic.height;
      return;
  }

  this.boundingBox.rectangle.coordinates = coords;
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
          ((coords.east - coords.west) / 2) + coords.west, coords.south, top);
        break;
      case 'bottom':
        bill.position = Cesium.Cartesian3.fromRadians(
          ((coords.east - coords.west) / 2) + coords.west, coords.south, bot);
        break;
    }
  }
}
