// Depends on /main/js/baseMap.js
// The MapViewer is the Cesium Map Viewer

var mapViewer;
var boundingBox;
var values;
var dragging = false;

// when document is ready, set up the map viewer
$(document).ready (function() {
  mapViewer = new MapViewer();
  mapViewer.setupMap({useSTKTerrain: true});
  var cviewer = mapViewer.getCesiumViewer();

  cviewer.homeButton.viewModel.command.beforeExecute
      .addEventListener(function(commandInfo){
    cviewer.flyTo(cviewer.entities);
    console.log("Returning camera to center position.");
    
    // Tell the home button not to do anything.
    commandInfo.cancel = true;
  });

  // remove jquery-ui styles and functionality from the cesium buttons
});

// given a values object which contains nesw and top/bottom values (in degrees
// and meters, respectively), create and display the bounding box
function createBoundingBox(v) {
  $(".cesium-button").button('destroy');
  document.getElementById('right').style.display = 'block';

  values = v;

  // make sure the values passed in are valid
  var v = validateBoundingBox(values);
  if (v !== "valid") {
    alert(v);
    return;
  }

  var cviewer = mapViewer.getCesiumViewer();
  var entities = cviewer.entities;
  var coords = new Cesium.Rectangle.fromDegrees(
    values.west, values.south, values.east, values.north);

  //if bounding box already exists, remove before creating a new one
  if (boundingBox) {
    entities.remove(boundingBox);
  }

  // add the bounding box entity
  boundingBox = entities.add({
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
      material : Cesium.Color.WHITE.withAlpha(0.2)
    },
    position : Cesium.Cartesian3.fromDegrees(values.west, values.south, values.top),
    name : "Bounding Box"
  });

  //initializeEditors(boundingBox);

  cviewer.zoomTo(entities);
  //or : cviewer.flyTo(entites);
}

function initializeEditors(boundingBox) {
  var viewer = mapViewer.getCesiumViewer();
  var drawHelper = new DrawHelper(viewer.cesiumWidget);
  var extent = boundingBox.rectangle.coordinates;

  console.log(extent);
  console.log('i can do this')

  var extentPrimitive = new DrawHelper.ExtentPrimitive({
    extent: extent,
    material: Cesium.Material.fromType(Cesium.Material.StripeType)
  })
  scene.primitives.add(extentPrimitive);
  extentPrimitive.setEditable();
  extentPrimitive.addListener('onEdited', function(event) {
    console.log('Extent edited: extent is (N: ' + event.extent.north.toFixed(3) + ', E: ' + event.extent.east.toFixed(3) + ', S: ' + event.extent.south.toFixed(3) + ', W: ' + event.extent.west.toFixed(3) + ')');
  });
}

/*function allowDrag(viewer, entity, height) {
  var mousePosition = new Cesium.Cartesian2();
  var mousePositionProperty = new Cesium.CallbackProperty(function(time, result){
    var position = scene.camera.pickEllipsoid(mousePosition, undefined, result);
    console.log('hello');
    var cartographic = Cesium.Ellipsoid.WGS84.cartesianToCartographic(position);
    cartographic.height = height;
    return Cesium.Ellipsoid.WGS84.cartographicToCartesian(cartographic);
  }, false);

  var scene = viewer.scene;
  var dragging = false;
  var handler = new Cesium.ScreenSpaceEventHandler(viewer.canvas);
  handler.setInputAction(
    function(click) {
      var pickedObject = scene.pick(click.position);
      if (Cesium.defined(pickedObject) && (pickedObject.id === entity)) {
        dragging = true;
        scene.screenSpaceCameraController.enableRotate = false;
        Cesium.Cartesian2.clone(click.position, mousePosition);
        entity.position = mousePositionProperty;  // this is what's not working; have to adjust for rectangle with set lat/lon
        //console.log(entity.position);
      }
    },
    Cesium.ScreenSpaceEventType.LEFT_DOWN
  );

  handler.setInputAction(
    function(movement) {
      if (dragging) {
        //Cesium.Cartesian2.clone(movement.endPosition, mousePosition);  // or this? not sure
      }
    },
    Cesium.ScreenSpaceEventType.MOUSE_MOVE
  );


  handler.setInputAction(
    function(click) {
      if(dragging) {
        dragging = false;
        scene.screenSpaceCameraController.enableRotate = true;

        var mypos = scene.camera.pickEllipsoid(click.position);
        var cartographic = Cesium.Ellipsoid.WGS84.cartesianToCartographic(mypos);
        cartographic.height = height;
        mypos = Cesium.Ellipsoid.WGS84.cartographicToCartesian(cartographic);
        entity.position = mypos;
      }
    },
    Cesium.ScreenSpaceEventType.LEFT_UP
  );
}*/

// given a form update event evt, update the bounding box appropriately
function updateBoundingBox(evt) {
  var target = evt.currentTarget.id;
  switch(target) {
    case "id_south_d":
    case "id_south_m":
      updateEdge('south');
      break;
    case "id_west_d":
    case "id_west_m":
      updateEdge('west');
      break;
    case "id_bottom_d":
    case "id_bottom_m":
      var bottom = document.getElementById("id_bottom_d").value;
      values.bottom = parseFloat(bottom);
      var v = validateBoundingBox(values);
      if (v !== "valid") {
        alert(v);
        return;
      }
      boundingBox.rectangle.height = bottom;
      boundingBox.rectangle.material = Cesium.Color.WHITE.withAlpha(0.2);
      mapViewer.getCesiumViewer().flyTo(mapViewer.getCesiumViewer().entities);
      break;
    case "id_north_d":
    case "id_north_m":
      updateEdge('north');
      break;
    case "id_east_d":
    case "id_east_m":
      updateEdge('east');
      break;
    case "id_top_d":
    case "id_top_m":
      var top = document.getElementById("id_top_d").value;
      values.top = parseFloat(top);
      var v = validateBoundingBox(values);
      if (v !== "valid") {
        alert(v);
        return;
      }
      boundingBox.rectangle.extrudedHeight = top;
      boundingBox.rectangle.material = Cesium.Color.WHITE.withAlpha(0.2);
      mapViewer.getCesiumViewer().flyTo(mapViewer.getCesiumViewer().entities);
      break;
  }
}

// given the name of an edge as a string (e.g. 'north'), update it with
// the new value for that edge from the form element
function updateEdge(edgeName) {
  var edge = document.getElementById("id_" + edgeName + "_d").value;
  values[edgeName] = parseFloat(edge);

  var v = validateBoundingBox(values);
  if (v !== "valid") {
    alert(v);
    return;
  }

  boundingBox.rectangle.coordinates._value[edgeName] = 
    Cesium.Math.toRadians(edge);
  boundingBox.rectangle.material = Cesium.Color.WHITE.withAlpha(0.2);
  mapViewer.getCesiumViewer().flyTo(mapViewer.getCesiumViewer().entities);
}

// given a values object holding nesw and top/bottom values, check that these
// values form a valid bounding box. if so, return 'valid'; otherwise return
// an informative error message.
function validateBoundingBox(values) {
  var north = values.north; var south = values.south;
  var west = values.west; var east = values.east;
  var top = values.top; var bottom = values.bottom;

  if (!north || !south || !west || !east || !top || !bottom) {
    return "Please make sure all values are filled in.";
  }

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