// Functionality for setting up the initial map view.
// Depends on /main/js/baseMap.js
// The MapViewer is the Cesium Map Viewer

var mapViewer;
var boundingBox;
var values;
var corners;
var prevValues;

// when document is ready, set up the map viewer
$(document).ready (function() {
  mapViewer = new MapViewer();
  mapViewer.setupMap({useSTKTerrain: true});
  var cviewer = mapViewer.getCesiumViewer();

  cviewer.homeButton.viewModel.command.beforeExecute.removeEventListener(goHome);

  cviewer.homeButton.viewModel.command.beforeExecute
      .addEventListener(function(commandInfo){
    cviewer.zoomTo(boundingBox);
    console.log("Returning camera to center position.");
    commandInfo.cancel = true;
  });
});

// given a values object which contains nesw and top/bottom values (in degrees
// and meters, respectively), create and display the bounding box
function createBoundingBox(v) {
  if ($(".cesium-button").button('instance')) {
    $(".cesium-button").button('destroy');
  }

  values = v;
  prevValues = $.extend({}, values);

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
      material : Cesium.Color.WHITE.withAlpha(0.2),
    },
    name : "Bounding Box"
  });

  boundingBox.description = "The bounding box specified here will determine " +
  "the boundaries of the scene containing all the voxels. An initial box was " +
  "pre-calculated during SFM processing to include most of the tie points " + 
  "while excluding outliers, but you can now change any of the values or " +
  "click and drag the image to update the bounding box estimates."

  // zoom to the bounding box and once it's there, set the map to visible
  document.getElementById('right').style.display = 'block';
  document.getElementById('right').style.visibility = 'hidden';
  cviewer.zoomTo(boundingBox).then(function(result){
    if (result) {
      document.getElementById('right').style.visibility = 'visible';
    }
  });

  setEditable(boundingBox);
}

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
        values = prevValues;
        document.getElementById("id_bottom_d").value = values.bottom;
        update_bbox_meter();
        return;
      }
      boundingBox.rectangle.height = bottom;
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
        values = prevValues;
        document.getElementById("id_top_d").value = values.top;
        update_bbox_meter();
        return;
      }
      boundingBox.rectangle.extrudedHeight = top;
      mapViewer.getCesiumViewer().zoomTo(mapViewer.getCesiumViewer().entities);
      break;
  }
  prevValues = $.extend({}, values);
  updateCorners();
}

// given the name of an edge as a string (e.g. 'north'), update it with
// the new value for that edge from the form element
function updateEdge(edgeName) {
  var edge = document.getElementById("id_" + edgeName + "_d").value;
  values[edgeName] = parseFloat(edge);

  var v = validateBoundingBox(values);
  if (v !== "valid") {
    alert(v);
    values = prevValues;
    document.getElementById("id_" + edgeName + "_d").value = values[edgeName];
    update_bbox_meter();
    return;
  }

  var coords = boundingBox.rectangle.coordinates.getValue();
  coords[edgeName] = Cesium.Math.toRadians(edge);
  boundingBox.rectangle.coordinates = coords;

  mapViewer.getCesiumViewer().zoomTo(boundingBox);
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