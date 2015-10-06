// Depends on /main/js/baseMap.js

MapViewer.prototype.initialize = function(config) { 
  this.setupMap(config);
  var that = this;
  
  // TODO Add entity list and support adding voxel cylinders to the map
};

MapViewer.prototype.addVoxel = function(lat, lon, alt, color) {
  var entities = this.cesiummap.entities;

  entities.add({
    position : Cesium.Cartesian3.fromDegrees(lon, lat, alt),
    ellipse : {
        semiMinorAxis : 10.0,
        semiMajorAxis : 10.0,
        extrudedHeight : 10.0,
        outline : true,
        outlineColor : Cesium.Color.WHITE,
        outlineWidth : 1,
//        material : Cesium.Color.fromCssColorString(color)
        material : Cesium.Color.fromRandom({alpha : 0.8})
    }
  }); 
  /*entities.add({
  position : Cesium.Cartesian3.fromDegrees(lon, lat),
    ellipse : {
        semiMinorAxis : 100000.0,
        semiMajorAxis : 200000.0,
        height : 100000.0,
        extrudedHeight : 200000.0,
        rotation : Cesium.Math.toRadians(90.0),
        material : Cesium.Color.fromRandom({alpha : 1.0})
    } 
  });*/
};
