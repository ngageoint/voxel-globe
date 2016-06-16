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
