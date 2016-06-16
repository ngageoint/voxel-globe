function MapViewer() {
}

/**
 * This method is intended to support set up of common map actions so all maps
 * in the UI will have the same behavior for common buttons, clicks, etc.
 */
MapViewer.prototype.setupMap = function(config) { 
  var that = this;
  var shouldRender = true;
  if (config.noRender) {
    shouldRender = false;
  }
  Cesium.BingMapsApi.defaultKey = "0zblO6y6G6YudavPx5Ec~J6IvJKffmtUaoUu71RtArQ~AkhMuWWBuZSBX3HMW_mzrsRa1kzdlXAjxvyzuXlcwb3lhbREm3QuK4m1ZxHw8JhU"

  var shouldGeocode = false;
  if (config.geocoder) {
    shouldGeocode = true;
  }

  // set up the map widget
  this.cesiummap = new Cesium.Viewer('mapWidget', {
    // imageryProvider : new Cesium.ArcGisMapServerImageryProvider({
    //   url : 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer'
    // }),
    useDefaultRenderLoop: shouldRender,
    fullscreenButton: false,
    animation: false,
    baseLayerPicker: true,
    geocoder: shouldGeocode,
    homeButton: true,
    sceneModePicker: false,
    selectionIndicator: false,
    timeline: false,
    navigationHelpButton: false,
    navigationInstructionsInitiallyVisible: false
  });

  // use STK terrain by default
  if (config.useSTKTerrain) {
    // pretty sure this code does not work
    var terrainProvider = new Cesium.CesiumTerrainProvider({
       url : '//assets.agi.com/stk-terrain/world'
    });
    this.cesiummap.terrainProvider = terrainProvider;
    // but this does! Use STK terrain by simulating click on that button.
    $(".cesium-baseLayerPicker-item")[16].click();
  }

  // disable the cesium buttons as jquery buttons, otherwise they look bad
  $(function() {
    if ($(".cesium-button").button('instance')) {
      $(".cesium-button").button('destroy');
    }
  })

/*
  var ellipsoid = Cesium.Ellipsoid.WGS84;
  var south = Cesium.Math.toRadians(this.centerLat - this.zoomLevel)
  var west = Cesium.Math.toRadians(this.centerLon - this.zoomLevel);
  var north = Cesium.Math.toRadians(this.centerLat + this.zoomLevel);
  var east = Cesium.Math.toRadians(this.centerLon + this.zoomLevel);

  var extent = new Cesium.Rectangle(west, south, east, north);
  this.cesiummap.scene.camera.viewRectangle(extent, ellipsoid); */
  // TODO : Use this to restore original view someday
  // this.originalTilt = this.cesiummap.scene.camera.tilt;
  // this.originalHeading = this.cesiummap.scene.camera.heading;
  // this originalDirection = this.
  // var direction = this.cesiummap.scene.camera.direction;
  // this.originalDirection = new Cesium.Cartesian3(direction.x, direction.y, direction.z);
  
  this.cesiummap.homeButton.viewModel.command.beforeExecute
      .addEventListener(function (commandInfo) {
    //Zoom to custom extent
    var camera = that.cesiummap.scene.camera;
    console.log("Returning camera to center position.");
    
    that.cesiummap.scene.camera.lookAtTransform(Cesium.Matrix4.IDENTITY);
    // changed 9/10/15, that.cesiummap.scene.camera.setTransform(Cesium.Matrix4.IDENTITY);

    /*console.log("Camera direction: " + camera.direction);
    console.log("Camera position: " + camera.position);
    console.log("Camera tilt: " + camera.tilt);
    
    camera.tilt = that.originalTilt;
    camera.heading = that.originalHeading;
    camera.direction.x = that.originalDirection.x;
    camera.direction.y = that.originalDirection.y;
    camera.direction.z = that.originalDirection.z;
    */
   
    that.viewHomeLocation();

    //Tell the home button not to do anything.
    commandInfo.cancel = true;
  }); 
}

MapViewer.prototype.getCesiumViewer = function() {
  return this.cesiummap;
}

MapViewer.prototype.viewHomeLocation = function() {
  var that = this;
  if (this.homeEntity != null) {
    this.cesiummap.zoomTo(this.homeEntity).then(function(result){
      if (result) {
        document.getElementById('right').style.visibility = 'visible';
      }
    });
  } else if (this.extent != null) {
    this.cesiummap.camera.setView({  // setView -> flyTo for animation
      destination : that.extent
    });
  } else if (this.center != null) {
    this.cesiummap.camera.setView({  // setView -> flyTo for animation
      destination : that.center
/*        orientation: {
        heading : 0.0,
        pitch : -Cesium.Math.PI_OVER_TWO,
        roll : 0.0
      } */
    });
  } else {
    console.log("No home location has been defined for the map...");
  }
} 

MapViewer.prototype.setBoundingRectangle = function(west, south, east, north) {
//var ellipsoid = Cesium.Ellipsoid.WGS84;
  var extent = Cesium.Rectangle.fromDegrees(west, south, east, north);
  this.extent = extent;
  console.log("Set the extent to " + south + ", " + west + " and " + north + ", " + east);
//  this.cesiummap.scene.camera.viewRectangle(this.extent, ellipsoid); 
  this.viewHomeLocation();
}

MapViewer.prototype.setHomeLocation = function(centerLat, centerLon, centerAlt) {
  this.centerLat = centerLat;
  this.centerLon = centerLon;
  this.centerAlt = centerAlt;

  this.center = Cesium.Cartesian3.fromDegrees(this.centerLon, 
    this.centerLat,
    this.centerAlt
  );
  /*this.zoomLevel = 0.07;
  var ellipsoid = Cesium.Ellipsoid.WGS84;
  var south = Cesium.Math.toRadians(this.centerLat - this.zoomLevel)
  var west = Cesium.Math.toRadians(this.centerLon - this.zoomLevel);
  var north = Cesium.Math.toRadians(this.centerLat + this.zoomLevel);
  var east = Cesium.Math.toRadians(this.centerLon + this.zoomLevel);

  this.extent = new Cesium.Rectangle(west, south, east, north);*/
  this.viewHomeLocation();
}

// If the map has a home entity defined, calling viewHomeLocation() will focus
// it on that entity (so you don't have to calculate the camera's location or
// bounding rectangle by hand, since cesium's zoomTo(entity) method does this
// automatically).
MapViewer.prototype.setHomeEntity = function(entity) {
  console.log("Set the home entity to " + entity.name);
  this.homeEntity = entity;
  this.viewHomeLocation();
}

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

  new Corner(coords.west, coords.south, top, corners, "swt", this);
  new Corner(coords.west, coords.north, top, corners, "nwt", this);
  new Corner(coords.west, coords.south, bot, corners, "swb", this);
  new Corner(coords.west, coords.north, bot, corners, "nwb", this);
  new Corner(coords.east, coords.south, top, corners, "set", this);
  new Corner(coords.east, coords.north, top, corners, "net", this);
  new Corner(coords.east, coords.south, bot, corners, "seb", this);
  new Corner(coords.east, coords.north, bot, corners, "neb", this);
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
            ((pickedObject.id[0] instanceof Corner) || 
            (pickedObject.id[0] instanceof Handle))) {
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

/* 
 * Models a Corner billboard. Given the lat, lon, and height, adds a billboard
 * with the corner.png icon to that position on the cesium globe, and adds
 * the billboard to the given Cesium.BillboardCollection. Listens for click
 * and drag events, upon which it updates its own position, the positions of
 * the other associated corners and the bounding box as a whole, and the numbers
 * in the form data.
 */
function Corner(long, lat, height, collection, name, mapViewer) {
  var viewer = mapViewer.getCesiumViewer();
  var scene = viewer.scene;
  var prev = {
    values: {},
    position: new Cesium.Cartesian3()
  }

  var corner = collection.add({
    position: new Cesium.Cartesian3.fromRadians(long, lat, height),
    image : iconFolderUrl + "corner.png",
    eyeOffset : new Cesium.Cartesian3(0, 0, -100),
    id : [this,name]
  });

  // click and drag listeners inspired by leforthomas's cesium-drawhelper,
  // https://github.com/leforthomas/cesium-drawhelper

  this.onClick = function(position) {
    enableRotation(false);

    // store the current values and position in prev object for error recovery
    prev.values = $.extend({}, mapViewer.values);
    prev.position = Cesium.Cartesian3.clone(corner.position);
  
    // When using the mouse position, it's necessary to first find the plane
    // that passes through this point and is parallel to the tangent plane on
    // the ellipsoid surface. Then find the intersection of this plane with the
    // pickRay defined by that position, so it doesn't always consider the
    // picked position to be on the surface of the globe.

    // based on a coplanar point and the normal vector, find the plane
    var coplanar = corner.position;
    var normal = new Cesium.Cartesian3();
    Cesium.Ellipsoid.WGS84.geocentricSurfaceNormal(coplanar, normal);
    var plane = Cesium.Plane.fromPointNormal(coplanar, normal);

    function onDrag(position) {
      var pickRay = scene.camera.getPickRay(position);
      // find the intersection of the plane and the pickRay; this is the new pos
      corner.position = Cesium.IntersectionTests.rayPlane(pickRay, plane);

      mapViewer.drawUpdateBoundingBox(corner.position, name);
      updateFormFields(mapViewer.values);
      mapViewer.updateCorners();
    }

    function onDragEnd() {
      handler.destroy();
      enableRotation(true);
      var v = mapViewer.validateBoundingBox(mapViewer.values);
      if (v !== "valid") {
        alert(v);
        // recover from the error by restoring the previous values
        mapViewer.values = prev.values;
        corner.position = prev.position;
        mapViewer.drawUpdateBoundingBox(corner.position, name);
        updateFormFields(mapViewer.values);
        mapViewer.updateCorners();
      }
    }

    var handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);

    handler.setInputAction(function(movement) {
      onDrag(movement.endPosition);
    }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);

    handler.setInputAction(function(movement) {
      onDragEnd(scene.camera.pickEllipsoid(movement.position));
    }, Cesium.ScreenSpaceEventType.LEFT_UP);
  }
}

/* 
 * Models a Handle billboard (the up/down arrows on the southern face of the 
 * bounding cube). Given the lat, lon, and height, adds a billboard
 * with the top or bottom.png icon to that position on the cesium globe, and 
 * adds the billboard to the given Cesium.BillboardCollection. Listens for click
 * and drag events, upon which it updates its own position, the positions of
 * the other associated corners and the bounding box as a whole, and the numbers
 * in the form data.
 */
function Handle(long, lat, height, collection, name, mapViewer) {
  var viewer = mapViewer.getCesiumViewer();
  var scene = viewer.scene;
  var prev = {
    values: {},
    position: new Cesium.Cartesian3()
  }

  var handle = collection.add({
    position: new Cesium.Cartesian3.fromRadians(long, lat, height),
    image : iconFolderUrl + name + ".png",
    eyeOffset : new Cesium.Cartesian3(0, 0, -100),
    id : [this,name]
  });

  this.onClick = function(position) {
    enableRotation(false);

    // store the current values and position in prev object for error recovery
    prev.values = $.extend({}, mapViewer.values);
    prev.position = Cesium.Cartesian3.clone(handle.position);

    // see above comment about finding the intersection plane. This time, for
    // the vertical height handlers, we want the perpendicular plane to the one
    // described above -- i.e. the plane represented by the front face of the
    // bounding cube.

    // find the plane using three coplanar points
    var a = handle.position;
    var b = collection.get(0).position;  // southwest top
    var c = collection.get(2).position;  // southwest bottom
    var v0 = subtract(a, b);  // subtract a from b and store in v0
    var v1 = subtract(c, b);  // subtract b from c and store in v1
    var normal = cross(b, a);  // compute cross-product of v0 and v1
    var plane = Cesium.Plane.fromPointNormal(a, normal, plane);

    // TODO: I defined subtract and cross myself, below, since not working
    // out of the box, probably bc cesium is out of date. should replace 
    // with the real cesium functions once it's updated.

    function onDrag(position) {
      var pickRay = scene.camera.getPickRay(position);
      var intersect = Cesium.IntersectionTests.rayPlane(pickRay, plane);

      handle.position = intersect;
      mapViewer.drawUpdateBoundingBox(handle.position, name)
      updateFormFields(mapViewer.values)
      mapViewer.updateCorners();
      var c = Cesium.Ellipsoid.WGS84.cartesianToCartographic(handle.position);
      if (c.height < -100) {
        onDragEnd();
      }
    }

    function onDragEnd() {
      handler.destroy();
      enableRotation(true);
      var v = mapViewer.validateBoundingBox(mapViewer.values);
      if (v !== "valid") {
        alert(v);
        // recover from the error by restoring the previous values
        mapViewer.values = prev.values;
        handle.position = prev.position;
        mapViewer.drawUpdateBoundingBox(handle.position, name);
        updateFormFields(mapViewer.values);
        mapViewer.updateCorners();
      }
    }

    var handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);

    handler.setInputAction(function(movement) {
      onDrag(movement.endPosition);
    }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);

    handler.setInputAction(function(movement) {
      onDragEnd(scene.camera.pickEllipsoid(movement.position));
    }, Cesium.ScreenSpaceEventType.LEFT_UP);
  }
}

function enableRotation(enable) {
  var scene = mapViewer.getCesiumViewer().scene;
  scene.screenSpaceCameraController.enableRotate = enable;
}

// TODO: I defined subtract and cross myself, below, since not working
// out of the box, probably bc cesium is out of date. should replace 
// with the real cesium functions once it's updated.

function subtract(left, right) {
  var result = new Cesium.Cartesian3();
  result.x = left.x - right.x;
  result.y = left.y - right.y;
  result.z = left.z - right.z;
  return result;
}

function cross(left, right) {
  var result = new Cesium.Cartesian3();
  var leftX = left.x;
  var leftY = left.y;
  var leftZ = left.z;
  var rightX = right.x;
  var rightY = right.y;
  var rightZ = right.z;

  var x = leftY * rightZ - leftZ * rightY;
  var y = leftZ * rightX - leftX * rightZ;
  var z = leftX * rightY - leftY * rightX;

  result.x = x;
  result.y = y;
  result.z = z;
  return result;
}
