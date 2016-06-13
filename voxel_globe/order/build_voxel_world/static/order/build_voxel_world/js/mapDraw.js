// Functionality for making the cube editable within the cesium map view.

function setEditable(entity) {
  var viewer = mapViewer.getCesiumViewer();

  // given an entity, find its coordinates, top and bottom
  var coords = entity.rectangle.coordinates.getValue();
  var top = entity.rectangle.extrudedHeight.getValue();
  var bot = entity.rectangle.height.getValue();

  // add billboards for each of its eight corners to the map
  if (corners) {
    corners.removeAll();
  }
  corners = new Cesium.BillboardCollection();
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
      var pickedPrimitives = viewer.scene.drillPick(click.position);
      var length = pickedPrimitives.length;

      for (i = 0; i < length; i++) {
        pickedObject = pickedPrimitives[i];
        if (Cesium.defined(pickedObject) && 
            ((pickedObject.id[0] instanceof Corner) || 
            (pickedObject.id[0] instanceof Handle))) {
          pickedObject.id[0].onClick(click.position);
          return;
        }
      }
    }, Cesium.ScreenSpaceEventType.LEFT_DOWN
  );
}

function Corner(long, lat, height, collection, name) {
  var viewer = mapViewer.getCesiumViewer();
  var scene = viewer.scene;
  var ellipsoid = scene.globe.ellipsoid;

  var corner = collection.add({
    position: new Cesium.Cartesian3.fromRadians(long, lat, height),
    horizontalOrigin : Cesium.HorizontalOrigin.CENTER,
    verticalOrigin : Cesium.VerticalOrigin.CENTER,
    image : iconFolderUrl + "corner.png",
    scaleByDistance : new Cesium.NearFarScalar(1.5e3, 0.1, 8.0e5, 0.0),
    eyeOffset : new Cesium.Cartesian3(0, 0, -100),
    id : [this,name]
  });

  // click and drag listeners inspired by leforthomas's cesium-drawhelper,
  // https://github.com/leforthomas/cesium-drawhelper

  this.onClick = function(position) {
    enableRotation(false);
    var coplanar = corner.position;
    var normal = new Cesium.Cartesian3();
    Cesium.Ellipsoid.WGS84.geocentricSurfaceNormal(coplanar, normal);
    var plane = Cesium.Plane.fromPointNormal(coplanar, normal);

    function onDrag(position) {
      var pickRay = scene.camera.getPickRay(position);
      var intersect = Cesium.IntersectionTests.rayPlane(pickRay, plane);
      corner.position = intersect;

      drawUpdateBoundingBox(corner.position, name);
      updateFormFields(values);
      updateCorners();
    }

    function onDragEnd() {
      handler.destroy();
      enableRotation(true);
    }

    var handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);

    handler.setInputAction(function(movement) {
      var cartesian = scene.camera.pickEllipsoid(movement.endPosition);
      if (cartesian) {
        onDrag(movement.endPosition);
      } else {
        onDragEnd();
      }
    }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);

    handler.setInputAction(function(movement) {
      onDragEnd(scene.camera.pickEllipsoid(movement.position));
    }, Cesium.ScreenSpaceEventType.LEFT_UP);
  }
}

function Handle(long, lat, height, collection, name) {
  var viewer = mapViewer.getCesiumViewer();
  var scene = viewer.scene;

  var handle = collection.add({
    position: new Cesium.Cartesian3.fromRadians(long, lat, height),
    horizontalOrigin : Cesium.HorizontalOrigin.CENTER,
    verticalOrigin : Cesium.VerticalOrigin.CENTER,
    image : iconFolderUrl + name + ".png",
    scaleByDistance : new Cesium.NearFarScalar(1.5e3, 0.5, 8.0e5, 0.0),
    eyeOffset : new Cesium.Cartesian3(0, 0, -100),
    id : [this,name]
  });

  this.onClick = function(position) {
    enableRotation(false);
    var coplanar = handle.position;
    var normal = Cesium.Ellipsoid.WGS84.geodeticSurfaceNormal(coplanar);
    console.log(normal);
    var plane = Cesium.Plane.fromPointNormal(coplanar, normal, plane);

    function onDrag(position) {
      var pickRay = scene.camera.getPickRay(position);
      console.log(plane);
      var intersect = Cesium.IntersectionTests.rayPlane(pickRay, plane);
      console.log(intersect);

      handle.position = intersect;

      var cartographic = Cesium.Ellipsoid.WGS84.cartesianToCartographic(
        handle.position);

      if (name == 'top') {
        boundingBox.rectangle.extrudedHeight = cartographic.height;
      } else if (name == 'bottom') {
        boundingBox.rectangle.height = cartographic.height;
      }
      
      values[name] = cartographic.height;

      var v = validateBoundingBox(values);
      if (v !== "valid") {
        alert(v);
        return;
      }

      updateFormFields(values)
      updateCorners();
    }

    function onDragEnd() {
      handler.destroy();
      enableRotation(true);
    }

    var handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);

    handler.setInputAction(function(movement) {
      var cartesian = scene.camera.pickEllipsoid(movement.endPosition);
      if (cartesian) {
        onDrag(movement.endPosition);
      } else {
        onDragEnd();
      }
    }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);

    handler.setInputAction(function(movement) {
      onDragEnd(scene.camera.pickEllipsoid(movement.position));
    }, Cesium.ScreenSpaceEventType.LEFT_UP);
  }
}

function drawUpdateBoundingBox(cartesian, name) {
  var cartographic = Cesium.Ellipsoid.WGS84.cartesianToCartographic(cartesian);
  var coords = boundingBox.rectangle.coordinates.getValue();

  switch(name) {
    case 'swt':
      values.west = Cesium.Math.toDegrees(cartographic.longitude);
      values.south = Cesium.Math.toDegrees(cartographic.latitude);

      var v = validateBoundingBox(values);
      if (v !== "valid") {
        alert(v);
        return;
      }

      coords.west = cartographic.longitude;
      coords.south = cartographic.latitude;
      break;
    case 'nwt':
      values.north = Cesium.Math.toDegrees(cartographic.latitude);
      values.west = Cesium.Math.toDegrees(cartographic.longitude);

      var v = validateBoundingBox(values);
      if (v !== "valid") {
        alert(v);
        return;
      }

      coords.north = cartographic.latitude;
      coords.west = cartographic.longitude;
      break;
    case 'swb':
      values.south = Cesium.Math.toDegrees(cartographic.latitude);
      values.west = Cesium.Math.toDegrees(cartographic.longitude);

      var v = validateBoundingBox(values);
      if (v !== "valid") {
        alert(v);
        return;
      }

      coords.south = cartographic.latitude;
      coords.west = cartographic.longitude;
      break;
    case 'nwb':
      values.north = Cesium.Math.toDegrees(cartographic.latitude);
      values.west = Cesium.Math.toDegrees(cartographic.longitude);

      var v = validateBoundingBox(values);
      if (v !== "valid") {
        alert(v);
        return;
      }

      coords.north = cartographic.latitude;
      coords.west = cartographic.longitude;
      break;
    case 'set':
      values.south = Cesium.Math.toDegrees(cartographic.latitude);
      values.east = Cesium.Math.toDegrees(cartographic.longitude);

      var v = validateBoundingBox(values);
      if (v !== "valid") {
        alert(v);
        return;
      }

      coords.south = cartographic.latitude;
      coords.east = cartographic.longitude;
      break;
    case 'net':
      values.north = Cesium.Math.toDegrees(cartographic.latitude);
      values.east = Cesium.Math.toDegrees(cartographic.longitude);

      var v = validateBoundingBox(values);
      if (v !== "valid") {
        alert(v);
        return;
      }

      coords.north = cartographic.latitude;
      coords.east = cartographic.longitude;
      break;
    case 'seb':
      values.south = Cesium.Math.toDegrees(cartographic.latitude);
      values.east = Cesium.Math.toDegrees(cartographic.longitude);

      var v = validateBoundingBox(values);
      if (v !== "valid") {
        alert(v);
        return;
      }

      coords.south = cartographic.latitude;
      coords.east = cartographic.longitude;
      break;
    case 'neb':
      values.north = Cesium.Math.toDegrees(cartographic.latitude);
      values.east = Cesium.Math.toDegrees(cartographic.longitude);

      var v = validateBoundingBox(values);
      if (v !== "valid") {
        alert(v);
        return;
      }

      coords.north = cartographic.latitude;
      coords.east = cartographic.longitude;
      break;
  }

  boundingBox.rectangle.coordinates = coords;
}

function updateCorners() {
  var coords = boundingBox.rectangle.coordinates.getValue();
  var top = boundingBox.rectangle.extrudedHeight.getValue();
  var bot = boundingBox.rectangle.height.getValue();
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