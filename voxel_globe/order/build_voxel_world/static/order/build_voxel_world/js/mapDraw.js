// Functionality for making the cube editable within the cesium map view.

function setEditable(entity) {
  var viewer = mapViewer.getCesiumViewer();

  // given an entity, find its coordinates, top and bottom
  var coords = entity.rectangle.coordinates.getValue();
  var top = entity.rectangle.extrudedHeight.getValue();
  var bot = entity.rectangle.height.getValue();

  // add billboards for each of its eight corners to the map
  var corners = new Cesium.BillboardCollection();
  new Corner(coords.west, coords.south, top, corners, "swt");
  new Corner(coords.west, coords.north, top, corners, "nwt");
  new Corner(coords.west, coords.south, bot, corners, "swb");
  new Corner(coords.west, coords.north, bot, corners, "nwb");
  new Corner(coords.east, coords.south, top, corners, "set");
  new Corner(coords.east, coords.north, top, corners, "net");
  new Corner(coords.east, coords.south, bot, corners, "seb");
  new Corner(coords.east, coords.north, bot, corners, "neb");
  viewer.scene.primitives.add(corners);

  // set up handlers that listen for clicks on the buttons
  var handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);

  handler.setInputAction(
    function (click) {
      var pickedObject = viewer.scene.pick(click.position);  // TODO drillpick
      if (Cesium.defined(pickedObject) && (pickedObject.id instanceof Corner)) {
        pickedObject.id.onClick(click.position);
      }
      
    }, Cesium.ScreenSpaceEventType.LEFT_DOWN
  );
}

function Corner(long, lat, height, collection, name) {
  var viewer = mapViewer.getCesiumViewer();
  var scene = viewer.scene;

  function enableRotation(enable) {
    viewer.scene.screenSpaceCameraController.enableRotate = enable;
  }

  var corner = collection.add({
    position: new Cesium.Cartesian3.fromRadians(long, lat, height),
    horizontalOrigin : Cesium.HorizontalOrigin.CENTER,
    verticalOrigin : Cesium.VerticalOrigin.CENTER,
    image : iconFolderUrl + "dragIcon.png",  // TODO
    height: 30,  // TODO
    width: 30,
    id : this
  });

  // click and drag listeners inspired by leforthomas's cesium-drawhelper,
  // https://github.com/leforthomas/cesium-drawhelper

  this.onClick = function(position) {
    console.log('you clicked ' + name);
    enableRotation(false);

    function onDrag(position) {
      corner.position = position;
      drawUpdateBoundingBox(position, name);
    }

    function onDragEnd(position) {
      handler.destroy();
      //viewer.flyTo(boundingBox);
      enableRotation(true);
    }

    var handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);

    handler.setInputAction(function(movement) {
      var cartesian = scene.camera.pickEllipsoid(movement.endPosition);  
      // TODO how to get this in three dimensions...?
      if (cartesian) {
        onDrag(cartesian);
      } else {
        onDragEnd(cartesian);
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

  // check name for neswtb
  if (name.indexOf('s') > -1) {
    coords.south = cartographic.latitude;
  }
  if (name.indexOf('n') > -1) {
    coords.north = cartographic.latitude;
  }
  if (name.indexOf('e') > -1) {
    coords.east = cartographic.longitude;
  }
  if (name.indexOf('w') > -1) {
    coords.west = cartographic.longitude;
  }

  boundingBox.rectangle.coordinates = coords;
  boundingBox.rectangle.material = Cesium.Color.WHITE.withAlpha(0.2);
}

function updateCorners() {

}