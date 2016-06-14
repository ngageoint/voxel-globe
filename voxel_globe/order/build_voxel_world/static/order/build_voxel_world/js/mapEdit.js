/* 
 * Functionality for making the cube editable within the cesium map view.
 * Given an entity, attaches draggable icons to each of its corners that can be
 * moved to adjust the bounding latitude and longitude of the box, and draggable
 * height handles for both top and bottom.
 */

function setEditable(entity) {
  var viewer = mapViewer.getCesiumViewer();
  //viewer.scene.globe.depthTestAgainstTerrain = false;

  // given an entity, find its coordinates, top and bottom
  var coords = entity.rectangle.coordinates.getValue();
  var top = entity.rectangle.extrudedHeight.getValue();
  var bot = entity.rectangle.height.getValue();

  // add billboards for each of its eight corners and up/down handles to the map
  if (corners) {
    corners.removeAll();
  } else {
    corners = new Cesium.BillboardCollection();
  }
  
  new Corner(coords.west, coords.south, top, corners, "swt");
  new Corner(coords.west, coords.north, top, corners, "nwt");
  new Corner(coords.west, coords.south, bot, corners, "swb");
  new Corner(coords.west, coords.north, bot, corners, "nwb");
  new Corner(coords.east, coords.south, top, corners, "set");
  new Corner(coords.east, coords.north, top, corners, "net");
  new Corner(coords.east, coords.south, bot, corners, "seb");
  new Corner(coords.east, coords.north, bot, corners, "neb");
  new Handle(((coords.east - coords.west) / 2) + coords.west, coords.south, top,
    corners, "top");
  new Handle(((coords.east - coords.west) / 2) + coords.west, coords.south, bot,
    corners, "bottom");
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
 * Models a Corner billboard. Given the lat, lon, and height, adds a billboard
 * with the corner.png icon to that position on the cesium globe, and adds
 * the billboard to the given Cesium.BillboardCollection. Listens for click
 * and drag events, upon which it updates its own position, the positions of
 * the other associated corners and the bounding box as a whole, and the numbers
 * in the form data.
 */
function Corner(long, lat, height, collection, name) {
  var viewer = mapViewer.getCesiumViewer();
  var scene = viewer.scene;
  var prev = {
    values: {},
    position: new Cesium.Cartesian3()
  }

  var corner = collection.add({
    position: new Cesium.Cartesian3.fromRadians(long, lat, height),
    image : iconFolderUrl + "corner4.png",
    eyeOffset : new Cesium.Cartesian3(0, 0, -100),
    id : [this,name]
  });

  // click and drag listeners inspired by leforthomas's cesium-drawhelper,
  // https://github.com/leforthomas/cesium-drawhelper

  this.onClick = function(position) {
    enableRotation(false);

    // store the current values and position in prev object for error recovery
    prev.values = $.extend({}, values);
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

      drawUpdateBoundingBox(corner.position, name);
      updateFormFields(values);
      updateCorners();
    }

    function onDragEnd() {
      handler.destroy();
      enableRotation(true);
      var v = validateBoundingBox(values);
      if (v !== "valid") {
        alert(v);
        // recover from the error by restoring the previous values
        values = prev.values;
        corner.position = prev.position;
        drawUpdateBoundingBox(corner.position, name);
        updateFormFields(values);
        updateCorners();
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
function Handle(long, lat, height, collection, name) {
  var viewer = mapViewer.getCesiumViewer();
  var scene = viewer.scene;
  var prev = {
    values: {},
    position: new Cesium.Cartesian3()
  }

  var handle = collection.add({
    position: new Cesium.Cartesian3.fromRadians(long, lat, height),
    image : iconFolderUrl + name + "2.png",
    eyeOffset : new Cesium.Cartesian3(0, 0, -100),
    id : [this,name]
  });

  this.onClick = function(position) {
    enableRotation(false);

    // store the current values and position in prev object for error recovery
    prev.values = $.extend({}, values);
    prev.position = Cesium.Cartesian3.clone(handle.position);

    // see above comment about finding the intersection plane. This time, for
    // the vertical height handlers, we want the perpendicular plane to the one
    // described above -- i.e. the plane represented by the front face of the
    // bounding cube.

    // find the plane using three coplanar points
    var a = handle.position;
    var b = corners.get(0).position;  // southwest top
    var c = corners.get(2).position;  // southwest bottom
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
      drawUpdateBoundingBox(handle.position, name)
      updateFormFields(values)
      updateCorners();
      var c = Cesium.Ellipsoid.WGS84.cartesianToCartographic(handle.position);
      if (c.height < -100) {
        onDragEnd();
      }
    }

    function onDragEnd() {
      handler.destroy();
      enableRotation(true);
      var v = validateBoundingBox(values);
      if (v !== "valid") {
        alert(v);
        // recover from the error by restoring the previous values
        values = prev.values;
        handle.position = prev.position;
        drawUpdateBoundingBox(handle.position, name);
        updateFormFields(values);
        updateCorners();
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
 * Given a new cartesian position and the name of the corner that has just been
 * moved (e.g. 'swt' for southwest top, etc.), update the white bounding box
 * visually on the screen, and also update the global values array.
 */
function drawUpdateBoundingBox(cartesian, name) {
  var cartographic = Cesium.Ellipsoid.WGS84.cartesianToCartographic(cartesian);
  var coords = boundingBox.rectangle.coordinates.getValue();

  switch(name) {
    case 'swt':
      values.west = Cesium.Math.toDegrees(cartographic.longitude);
      values.south = Cesium.Math.toDegrees(cartographic.latitude);
      coords.west = cartographic.longitude;
      coords.south = cartographic.latitude;
      break;
    case 'nwt':
      values.north = Cesium.Math.toDegrees(cartographic.latitude);
      values.west = Cesium.Math.toDegrees(cartographic.longitude);
      coords.north = cartographic.latitude;
      coords.west = cartographic.longitude;
      break;
    case 'swb':
      values.south = Cesium.Math.toDegrees(cartographic.latitude);
      values.west = Cesium.Math.toDegrees(cartographic.longitude);
      coords.south = cartographic.latitude;
      coords.west = cartographic.longitude;
      break;
    case 'nwb':
      values.north = Cesium.Math.toDegrees(cartographic.latitude);
      values.west = Cesium.Math.toDegrees(cartographic.longitude);
      coords.north = cartographic.latitude;
      coords.west = cartographic.longitude;
      break;
    case 'set':
      values.south = Cesium.Math.toDegrees(cartographic.latitude);
      values.east = Cesium.Math.toDegrees(cartographic.longitude);
      coords.south = cartographic.latitude;
      coords.east = cartographic.longitude;
      break;
    case 'net':
      values.north = Cesium.Math.toDegrees(cartographic.latitude);
      values.east = Cesium.Math.toDegrees(cartographic.longitude);
      coords.north = cartographic.latitude;
      coords.east = cartographic.longitude;
      break;
    case 'seb':
      values.south = Cesium.Math.toDegrees(cartographic.latitude);
      values.east = Cesium.Math.toDegrees(cartographic.longitude);
      coords.south = cartographic.latitude;
      coords.east = cartographic.longitude;
      break;
    case 'neb':
      values.north = Cesium.Math.toDegrees(cartographic.latitude);
      values.east = Cesium.Math.toDegrees(cartographic.longitude);
      coords.north = cartographic.latitude;
      coords.east = cartographic.longitude;
      break;
    case 'top':
      boundingBox.rectangle.extrudedHeight = cartographic.height;
      values.top = cartographic.height;
      return;
    case 'bottom':
      boundingBox.rectangle.height = cartographic.height;
      values.bottom = cartographic.height;
      return;
  }

  boundingBox.rectangle.coordinates = coords;
}

/*
 * Once one corner or handle has been changed, update the rest as well to 
 * reflect the new positions of the bounding box.
 */
function updateCorners() {
  var coords = boundingBox.rectangle.coordinates.getValue();
  var top = boundingBox.rectangle.extrudedHeight.getValue();
  var bot = boundingBox.rectangle.height.getValue();

  // using a scratch variable is faster here than constantly defining a new
  var scratchPosition = new Cesium.Cartesian3;
  var ellipsoid = mapViewer.getCesiumViewer().scene.mapProjection.ellipsoid;

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

// https://groups.google.com/forum/#!topic/cesium-dev/_VXb_CNRlLM
var cameraHeight = -1;
var eyeOffsetCallback = new Cesium.CallbackProperty(function() {
  var zIndex = -1;
  var currCameraHeight = viewer.camera.positionCartographic.height;
  console.log(currCameraHeight);
  if (currCameraHeight  > 85000 && cameraHeight <= 85000) {
    zIndex = -10000;
  }
  if (currCameraHeight  <= 85000 && currCameraHeight >= 500 && (cameraHeight <= 500 || cameraHeight > 85000)) {
    zIndex = -500;
  }
  if (currCameraHeight  <= 500 && cameraHeight > 500) {
    zIndex = -100;
  }
  if (zIndex == -1) {
   return this;
  }
  return new Cesium.Cartesian3(0.0, 0.0, zIndex);
}, false);


/*
var eyeOffsetCallback = new Cesium.CallbackProperty(function(){
  var zIndex = -1;
  var currCameraHeight = viewer.camera.positionCartographic.height;
  if (currCameraHeight  > 85000 && cameraHeight <= 85000) {
    zIndex = -10000;
  }
  if (currCameraHeight  <= 85000 && currCameraHeight >= 500 && (cameraHeight <= 500 || cameraHeight > 85000) {
    zIndex = -500;
  }
  if (currCameraHeight  <= 500 && cameraHeight > 500) {
    zIndex = -100;
  }
  if (zIndex == -1) {
   return this;
  }
  return new Cesium.Cartesian3(0.0, 0.0, zIndex);
}, false);

*/