function MapViewer() {
}

/**
 This method is intended to support set up of common map actions so all maps in the UI
 will have the same behavior for common buttons, clicks, etc.
**/
MapViewer.prototype.setupMap = function(config) { 
  var that = this;
  this.centerLat = config.latitude;
  this.centerLon = config.longitude;
  this.zoomLevel = config.zoomLevel;
  Cesium.BingMapsApi.defaultKey = "0zblO6y6G6YudavPx5Ec~J6IvJKffmtUaoUu71RtArQ~AkhMuWWBuZSBX3HMW_mzrsRa1kzdlXAjxvyzuXlcwb3lhbREm3QuK4m1ZxHw8JhU"
  this.cesiummap = new Cesium.Viewer('mapWidget', {timeline: false, 
    fullscreenButton : false, homeButton : true, 
    animation : false,
 //   imageryProvider : new Cesium.ArcGisMapServerImageryProvider({
 //       url : 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer'
 //     }),
    baseLayerPicker : true
  });
    
  var terrainProvider = new Cesium.CesiumTerrainProvider({
    url : '//assets.agi.com/stk-terrain/world'
  });
  this.cesiummap.terrainProvider = terrainProvider;


  var ellipsoid = Cesium.Ellipsoid.WGS84;
  var south = Cesium.Math.toRadians(this.centerLat - this.zoomLevel)
  var west = Cesium.Math.toRadians(this.centerLon - this.zoomLevel);
  var north = Cesium.Math.toRadians(this.centerLat + this.zoomLevel);
  var east = Cesium.Math.toRadians(this.centerLon + this.zoomLevel);

  var extent = new Cesium.Rectangle(west, south, east, north);
  this.cesiummap.scene.camera.viewRectangle(extent, ellipsoid);
  // TODO : Use this to restore original view someday
  // this.originalTilt = this.cesiummap.scene.camera.tilt;
  // this.originalHeading = this.cesiummap.scene.camera.heading;
  // this originalDirection = this.
  // var direction = this.cesiummap.scene.camera.direction;
  // this.originalDirection = new Cesium.Cartesian3(direction.x, direction.y, direction.z);
  
  this.cesiummap.homeButton.viewModel.command.beforeExecute.addEventListener(function(commandInfo){
    //Zoom to custom extent
    var camera = that.cesiummap.scene.camera;
    console.log("Returning camera to home position.");
    
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
    that.cesiummap.scene.camera.viewRectangle(extent, ellipsoid);

    //Tell the home button not to do anything.
    commandInfo.cancel = true;
  });
}