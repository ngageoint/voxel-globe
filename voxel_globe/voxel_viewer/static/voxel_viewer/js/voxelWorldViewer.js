
function VoxelWorldViewer() {

}


VoxelWorldViewer.prototype.loadVoxelWorld = function(voxelWorldParams) {
  // TODO, use voxel world information to set up the map...
  // TODO: Figure out how to get initial region for the map
  this.initializeMap({useSTKTerrain : true});
  console.log("Setting map home to " + voxelWorldParams.latitude +  ', ' + voxelWorldParams.longitude);
  this.mapViewer.setHomeLocation(voxelWorldParams.latitude, voxelWorldParams.longitude, 1000);

  this.pullData(voxelWorldParams);
  console.log("Loaded voxel world, id=" + voxelWorldParams.worldId);
}

/**
* This method creates the individual voxel objects that will be rendered
**/
VoxelWorldViewer.prototype.loadWorldData = function(rawData) {
  for (var i = 0; i < rawData.latitude.length; i++) {
    this.mapViewer.addVoxel(rawData.latitude[i], rawData.longitude[i], rawData.altitude[i], rawData.color[i], rawData.le[i], rawData.ce[i]);
  }
 }

/**
* This method fetches all of the requested Voxel World data from the DB
**/
VoxelWorldViewer.prototype.pullData = function(voxelWorldParams) {
  var that = this;
  var args = {};
  args['pointCloudId'] = voxelWorldParams.worldId;
  // Optional arguments for generating random worlds...
  if (voxelWorldParams['numPts'] != null) {
    args['points'] = voxelWorldParams.numPts;  
  }
  if (voxelWorldParams['centerLat'] != null) {
    args['latitude'] = voxelWorldParams.centerLat;  
  }
  if (voxelWorldParams['centerLon'] != null) {
    args['longitude'] = voxelWorldParams.centerLon;  
  }
  if (voxelWorldParams['centerAlt'] != null) {
    args['altitude'] = voxelWorldParams.centerAlt;  
  }
  console.log("fetching point cloud with args: points=" + args['points'] + " pointCloudId=" + args['pointCloudId']);
  // End optional arguments
  $.ajax({
    type : "GET",
    url : "/apps/voxel_viewer/fetchPointCloud",
    data : args,
    success : function(data) {
      if (data.errorMessage) {
        alert(data.errorMessage);
      } else {
          if (data.isRandom == true) {
            console.log("Displaying Random Data");
            $('#debugInfo').html("Displaying Random Data");
          } else {
            $('#debugInfo').html("Displaying Voxel World Id: " + voxelWorldParams.worldId);
          }
          that.loadWorldData(data);

      }
    },
    dataType : 'json'
  });
}

VoxelWorldViewer.prototype.initializeEvents = function() {
  // Set up the initial state
  this.showHideImageDisplay(); // make map display consistent with checkbox
  var that = this;
  $('#editorContentDiv').css("height", $(window).height() - 170 + "px");
  $('#editorContentDiv').css("width", 100 + "%");
  $(window).resize(function(e) {
    $('#editorContentDiv').css("height", $(window).height() - 170 + "px");
    $('#editorContentDiv').css("width",  100 + "%");
  });

  $('#showImage').click(function(e) {
    that.showImage();
  });
  
  $('#printDebugBtn').click(function(e) {
    var text = "Placeholder for some debug info...";
    $('#debugInfo').html(text);
  });
  
  $('#advancedOptionsDiv').toggle(false);
  $('#showAdvancedOptions').click(function (e) {
    $('#showAdvancedOptions').toggle(false);
    $('#advancedOptionsDiv').toggle(true);
  });
  
  $('#hideAdvancedOptions').click(function (e) {
    $('#advancedOptionsDiv').toggle(false);
    $('#showAdvancedOptions').toggle(true);
  });

  $('#loadAllPoints').click(function (e) {
    $('#loadNPoints').prop("checked", false);
    $('#loadAllPoints').prop("checked", true);
  });

  $('#loadNPoints').click(function (e) {
    $('#loadAllPoints').prop("checked", false);
    $('#loadNPoints').prop("checked", true);
  });

    $('#loadAllPoints').prop("checked", false);
    $('#loadNPoints').prop("checked", true);
};

VoxelWorldViewer.prototype.initializeMap = function(mapConfig) {
  this.mapViewer = new MapViewer();
  this.mapViewer.initialize(mapConfig);
};


VoxelWorldViewer.prototype.showHideImageDisplay = function() {
  console.log("Changing image display");
  if ($('#showImage').prop("checked")) {
    $('#sideBuffer').toggle(false);
    $('#mapContainer').css("width", "61%");
    $('#imageContainer').toggle(true);
  } else {
    $('#imageContainer').toggle(false);
    $('#sideBuffer').toggle(true);
    $('#mapContainer').css("width", "95%");
  }
};

VoxelWorldViewer.prototype.showImage = function() {
  // TODO wire up
  alert("Not yet implemented");
  console.log("Image needs to be loaded from the DB - have to figure out the API there");
  this.showHideImageDisplay();
}