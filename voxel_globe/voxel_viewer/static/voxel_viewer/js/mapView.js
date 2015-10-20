// Depends on /main/js/baseMap.js

MapViewer.prototype.initialize = function(config) { 
  this.setupMap(config);
  var that = this;
  this.voxelPointUrl = iconFolderUrl + "voxel2D.png";
  this.selectedVoxelPointUrl = iconFolderUrl + "voxel2D_highlight.png";
  this.selectedVoxel = null;


  // TODO Add entity list and support adding voxel cylinders to the map
//  var primitives = this.cesiummap.scene.primitives;
  var primitives = this.cesiummap.scene.primitives;
  this.voxelPointsBB = primitives.add(new Cesium.BillboardCollection());
  this.selectedVoxelPointsBB = primitives.add(new Cesium.BillboardCollection());

  this.selectedBillboard = this.selectedVoxelPointsBB.add( {
      position : Cesium.Cartesian3.fromDegrees(0, 0),
      show : true,
      horizontalOrigin : Cesium.HorizontalOrigin.CENTER,
      verticalOrigin : Cesium.VerticalOrigin.CENTER,
      image : this.selectedVoxelPointUrl,
      scale : 0.2
    });
  
  // If the mouse is clicked on a billboard, pop up details and highlight the billboard
  var handler = new Cesium.ScreenSpaceEventHandler(this.cesiummap.scene.canvas);
  handler.setInputAction(
        function (movement) {
                var pickedObject = that.cesiummap.scene.pick(movement.position);
                if (pickedObject != null && pickedObject.primitive != null) {
                  if (pickedObject.primitive.voxel) {
                    console.log("Trying to select a voxel on the map " + pickedObject.primitive.voxel);                    
                    that.setActiveVoxel(pickedObject.primitive);
                  } else {
                    that.clearSelectedVoxel();                    
                  }
                } else {
                  that.clearSelectedVoxel();
                }
            },
        Cesium.ScreenSpaceEventType.LEFT_CLICK
  );

  this.maxAltitude = 0.0;
  this.infoBoxEntity = new Cesium.Entity("Selected Voxel");
  this.infoBoxEntity.name = "Selected Voxel";
  this.infoBoxEntity.description = {
    getValue : function() {
        var htmlDesc = '<b>Latitude: </b>' + that.selectedVoxel.voxel.latitude + "<br>";
        
        htmlDesc += '<b>Longitude: </b>' + that.selectedVoxel.voxel.longitude + "<br>";
        htmlDesc += '<b>Altitude: </b> ' + that.selectedVoxel.voxel.altitude + "<br>";
        htmlDesc += '<b>LE: </b>' + that.selectedVoxel.voxel.le + "<br>";
        htmlDesc += '<b>CE: </b>' + that.selectedVoxel.voxel.ce + "<br>";

        return htmlDesc;
      }
    };

  this.cesiummap.infoBox.viewModel.showInfo = true;
  this.cesiummap.selectedEntity = undefined;

};

MapViewer.prototype.addVoxel = function(lat, lon, alt, color, le, ce) {
  var position = Cesium.Cartesian3.fromDegrees(lon, lat, alt);
  if (this.maxAltitude < alt) {
    this.maxAltitude = alt + 1; // 1 meter higher than max
  }

  var billboard = this.voxelPointsBB.add( {
      position : position,      
      horizontalOrigin : Cesium.HorizontalOrigin.CENTER,
      verticalOrigin : Cesium.VerticalOrigin.CENTER,
      image : this.voxelPointUrl,
      scale : 0.10,
//      color : Cesium.Color.fromRandom({alpha : 0.8})
      color : Cesium.Color.fromCssColorString(color)
    });
  billboard.eyeOffset = new Cesium.Cartesian3(0, 0, 0);
  billboard.voxel = {'latitude': lat, 'longitude': lon, 'altitude': alt, 'color' : color, "le" : le, "ce" : ce};
};

MapViewer.prototype.clearSelectedVoxel = function() {
  this.selectedVoxel = null;
  this.selectedBillboard.show = false;
  this.cesiummap.selectedEntity = undefined;
}

MapViewer.prototype.setActiveVoxel = function(voxelBB) {
  this.selectedVoxel = voxelBB;  
  this.selectedBillboard.position = voxelBB.position;
  this.selectedBillboard.eyeOffset = new Cesium.Cartesian3(0, 0, -10);
  this.selectedBillboard.voxel = voxelBB.voxel;    
  this.selectedBillboard.show = true;
  this.cesiummap.selectedEntity = this.infoBoxEntity;
};
