
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
    // if (typeof v === "string") {
      alert(v);
      return;
    // } else {
    //   // if a values object is returned, it means we had to switch values
    //   // e.g. north became south, so replace the old values, update the form
    //   // fields, and redraw the box based on the new values
    //   this.values = v;
    //   this.prevValues = $.extend({}, v);
    //   console.log(v);
    //   updateFormFields(this.values);
    // }
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
    if (typeof v === "string") {
      alert(v);
      document.getElementById("id_" + edgeName + "_d").value = this.values[edgeName];
      if (document.getElementById("id_" + edgeName + "_m")) {
        update_bbox_meter();
      }
      return;
    }
    // } else {
    //   // if a values object is returned, it means we had to switch values
    //   // e.g. north became south, so replace the old values, update the form
    //   // fields, and redraw the box based on the new values
    //   this.values = v;
    //   updateFormFields(this.values);
    // }
  } else {
    this.values = tempValues;
  }
}

// given a values object holding nesw and top/bottom values, check that these
// values form a valid bounding box. if so, return 'valid'; otherwise return
// an informative error message.
// if adjust == true, instead of alerting and returning, switch the invalid
// values.
MapViewer.prototype.validateBoundingBox = function(values, adjust) {
  var north = values.north; var south = values.south;
  var west = values.west; var east = values.east;
  var top = values.top; var bottom = values.bottom;

  if (top == bottom) {
    return "Top and bottom altitudes must not be equal."
  }

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

  if (east == west) {
    // if (adjust) {
    //   values.west = values.west + 0.0001;
    //   console.log('adjusting'); // TODO
    //   return values;
    // } else {
      return "East and west longitude must not be equal.";
    // }
  }

  if (top < bottom) {
    if (adjust) {
      var temp = values.top;
      values.top = values.bottom;
      values.bottom = temp;
      return values;
    } else {
      return "Top altitude must be greater than bottom altitude.";
    }
  }

  var changed = false;

  if (north < south) {
    if (adjust) {
      console.log('start');
      console.log(values);
      var temp = values.north;
      values.north = values.south;
      values.south = temp;
      console.log('end');
      console.log(values);
      console.log('');
      changed = true;
      // don't return values here because next we check validity of east/west
    } else {
      return "North latitude must be greater than south latitude.";
    }
  }

  var e = Cesium.Math.toRadians(east);
  var w = Cesium.Math.toRadians(west);

  // international date line
  if ((e > 0 && w < 0 && e - w > Cesium.Math.PI) ||
      (e < 0 && w > 0 && w - e > Cesium.Math.PI) ||
      e < w) {
    if (adjust) {
      changed = true;
      var temp = values.east;
      values.east = values.west;
      values.west = temp;
    }
  }

  if (changed) {
    return values;
  } else {
    return "valid";
  }
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
  var values = $.extend({}, this.values);

  if (name == "top") {
    values.top = cartographic.height;
  }

  if (name == "bottom") {
    values.bottom = cartographic.height;
  }

  if (containsChar(name, 's')) {
    values.south = Cesium.Math.toDegrees(cartographic.latitude);
  }

  if (containsChar(name, 'n')) {
    values.north = Cesium.Math.toDegrees(cartographic.latitude);
  }

  if (containsChar(name, 'e')) {
    values.east = Cesium.Math.toDegrees(cartographic.longitude);
  }

  if (containsChar(name, 'w')) {
    values.west = Cesium.Math.toDegrees(cartographic.longitude);
  }

  // var v = this.validateBoundingBox(values, true);
  // if (v !== "valid") {
  //   if (typeof v === "string") {
  //     alert(v);
  //     return;
  //   } else {
  //     values = v;
  //   }
  // }

  this.values = values;

  function containsChar(string, char) {
    if (string.indexOf(char) > -1) {
      return true;
    } else {
      return false;
    }
  }

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
