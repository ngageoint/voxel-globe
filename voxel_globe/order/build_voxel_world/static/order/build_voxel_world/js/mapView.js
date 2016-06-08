// Depends on /main/js/baseMap.js
// The MapViewer is the Cesium Map Viewer

var mapViewer;
var boundingBox;
var values;

function createBoundingBox(v) {
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

  //if bounding box already exists, remove it to create a new one
  if (boundingBox) {
    entities.remove(boundingBox);
  }

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
    name : "Bounding Box"
  });
  var promise = cviewer.zoomTo(entities);

  document.getElementById('right').style.display = 'block';

  // Listen for user clicks on the bounding box TODO
  var handler = new Cesium.ScreenSpaceEventHandler(cviewer.scene.canvas);
  handler.setInputAction(
    function (movement) {
        var pickedObject = cviewer.scene.pick(movement.position);
        console.log(movement);
        console.log(pickedObject);
      },
    Cesium.ScreenSpaceEventType.LEFT_CLICK
  );
}

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
      mapViewer.getCesiumViewer().zoomTo(mapViewer.getCesiumViewer().entities);
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
      mapViewer.getCesiumViewer().zoomTo(mapViewer.getCesiumViewer().entities);
      break;
  }
}

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
  mapViewer.getCesiumViewer().zoomTo(mapViewer.getCesiumViewer().entities);
}

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

$(document).ready (function() {
  mapViewer = new MapViewer();
  mapViewer.setupMap({useSTKTerrain: true});
})