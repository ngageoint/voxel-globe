function MapViewer(config) {
	this.centerLat = config.latitude;
	this.centerLon = config.longitude;
	this.zoomLevel = config.zoomLevel;
	this.inactiveCtrlPointUrl = iconFolderUrl + "inactiveCtrlPt.png";
	this.activeCtrlPointUrl = iconFolderUrl + "activeCtrlPt.png";
	this.inactiveTiePointUrl = iconFolderUrl + "inactiveTiePt.png";
	this.activeTiePointUrl = iconFolderUrl + "activeTiePt.png";
	this.cameraUrl = iconFolderUrl + "small-camera.png";
	this.frustumColor = new Cesium.Color(1.0, 1.0, 1.0, 0.6);
	this.activeRayColor = new Cesium.Color(1.0, 1.0, 0.0, 0.9);
 	this.inactiveRayColor = new Cesium.Color(0.45, 0.8, 1.0, 0.75);

	this.lastSelected = null;
	this.selectedCtrlPt = null;
	this.lastSelectedTiePoints = null;
	
	this.controlPointRefs = {};
	this.cameraFrustums = [];
	this.tiePointRays = {};
}

MapViewer.prototype.initialize = function() {	
	var that = this;
	this.cesiummap = new Cesium.Viewer('mapWidget', {timeline: false, 
		fullscreenButton : false, homeButton : true, 
		animation : false });
		
	var ellipsoid = Cesium.Ellipsoid.WGS84;
	var south = Cesium.Math.toRadians(this.centerLat - this.zoomLevel)
	var west = Cesium.Math.toRadians(this.centerLon - this.zoomLevel);
	var north = Cesium.Math.toRadians(this.centerLat + this.zoomLevel);
	var east = Cesium.Math.toRadians(this.centerLon + this.zoomLevel);

	var extent = new Cesium.Rectangle(west, south, east, north);
	this.cesiummap.scene.camera.viewRectangle(extent, ellipsoid);
	this.originalTilt = this.cesiummap.scene.camera.tilt;
	this.originalHeading = this.cesiummap.scene.camera.heading;
	var direction = this.cesiummap.scene.camera.direction;
	this.originalDirection = new Cesium.Cartesian3(direction.x, direction.y, direction.z);
	
	// Create a billboard collections
	var primitives = this.cesiummap.scene.primitives;
	this.controlPointBillboards = primitives.add(new Cesium.BillboardCollection());
	this.cameraBillboards = primitives.add(new Cesium.BillboardCollection());
	this.cameraFrustrumPolylines = primitives.add(new Cesium.PolylineCollection());
	this.tiePointPolylines = primitives.add(new Cesium.PolylineCollection());

	
	this.cesiummap.homeButton.viewModel.command.beforeExecute.addEventListener(function(commandInfo){
		//Zoom to custom extent
		var camera = that.cesiummap.scene.camera;
		console.log("Returning camera to home position.");
		
		that.cesiummap.scene.camera.setTransform(Cesium.Matrix4.IDENTITY);

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
	
	// If the mouse is over the billboard, change its scale and color
    var handler = new Cesium.ScreenSpaceEventHandler(this.cesiummap.scene.canvas);
    handler.setInputAction(
        function (movement) {
                var pickedObject = that.cesiummap.scene.pick(movement.position);
                if (pickedObject != null && pickedObject.primitive != null) {
                	if (pickedObject.primitive.controlPoint) {
                		console.log("Trying to select image on the map - controlPoint " + pickedObject.primitive.controlPoint.id);                   	
                		mainViewer.globalSelectControlPoint(pickedObject.primitive.controlPoint);
                    } else if (pickedObject.primitive.isCamera) {
                    	console.log("Trying to pick a camera and see it as though we are at the camera location..." + pickedObject.primitive.position);
                    	var loc = new Cesium.Cartesian3(pickedObject.primitive.position.x, pickedObject.primitive.position.y, pickedObject.primitive.position.z)
                        that.setReferenceFrame(loc);              	
                    }
                }
            },
        Cesium.ScreenSpaceEventType.LEFT_CLICK
    );

}

MapViewer.prototype.setReferenceFrame = function(location) {
    var center = location;
    console.log(center)
    var transform = Cesium.Transforms.eastNorthUpToFixedFrame(center);

    // View in east-north-up frame
    var camera = this.cesiummap.scene.camera;
    Cesium.Matrix4.clone(transform, camera.transform);
    camera.constrainedAxis = Cesium.Cartesian3.UNIT_Z;

    // Zoom in
    camera.lookAt(
        new Cesium.Cartesian3(-10.0, -10.0, 10.0),
        Cesium.Cartesian3.ZERO,
        Cesium.Cartesian3.UNIT_Z);
    
//
//    // Show reference frame.  Not required.
//    that.scene.primitives.add(new Cesium.DebugModelMatrixPrimitive({
//        modelMatrix : transform,
//        length : 1000.0
//    }));
}


MapViewer.prototype.addControlPoint = function(controlPoint) {	
	var position = Cesium.Cartesian3.fromDegrees(controlPoint.lon, controlPoint.lat, controlPoint.alt);
	//position.z = ;
	
	var billboard = this.controlPointBillboards.add( {
		  position : position,
		  horizontalOrigin : Cesium.HorizontalOrigin.CENTER,
		  verticalOrigin : Cesium.VerticalOrigin.CENTER,
		  image : this.inactiveCtrlPointUrl
		});
	billboard.controlPoint = controlPoint;
	
	this.controlPointRefs[controlPoint.id] = { cp : controlPoint, bb : billboard };	
}

MapViewer.prototype.removeControlPoint = function(controlPoint) {	
	
	var data = this.controlPointRefs[controlPoint.id];
	if (data) {
		var billboard = data.bb;
		if (billboard) {
			if (this.lastSelected == data.bb) {
				this.lastSelected = null;
			}
			this.controlPointBillboards.remove(billboard);
		}
		delete this.controlPointRefs[controlPoint.id];
	} else {
		console.log("No map data for control point " + controlPoint.name);
	}
}

MapViewer.prototype.addCamera = function(img) {	
	this.cesiummap.scene.camera.setTransform(Cesium.Matrix4.IDENTITY);
	var frustumSize = parseFloat($('#frustumSize').val());
	//var items = document.getElementById('historySelection');
	//var selectedHistory = parseInt(items.options[items.selectedIndex].value);
	var that = this;
	//console.log("Fetching camera frustum for image " + img.id + " - size " + frustumSize + " history " + selectedHistory);

	$.ajax({
		type : "GET",
		url : "/apps/tiepoint/fetchCameraFrustum",
		data : {
			imageId : img.id,
			size : frustumSize,
//			history : selectedHistory
		},
		success : function(data) {
			console.log("Retrieved camera frustum for image "
					+ img.id);
			if (mainViewer.displayCounter != img.displayCounter) {
				console.log("Image camera out of date, ignoring result..." + img.id);
				return;
			}
			var cameraFrustum = {};
			cameraFrustum.cameraLoc = { lat : data.lat[0], lon : data.lon[0], h : data.h[0] };
			cameraFrustum.f1 = { lat : data.lat[1], lon : data.lon[1], h : data.h[1] };
			cameraFrustum.f2 = { lat : data.lat[2], lon : data.lon[2], h : data.h[2] };
			cameraFrustum.f3 = { lat : data.lat[3], lon : data.lon[3], h : data.h[3] };
			cameraFrustum.f4 = { lat : data.lat[4], lon : data.lon[4], h : data.h[4] };
			
			var position = Cesium.Cartesian3.fromDegrees(cameraFrustum.cameraLoc.lon, cameraFrustum.cameraLoc.lat, cameraFrustum.cameraLoc.h);
			
			// Add a billboard for the camera
			var billboard = that.cameraBillboards.add( {
				  position : position,
				  horizontalOrigin : Cesium.HorizontalOrigin.CENTER,
				  verticalOrigin : Cesium.VerticalOrigin.CENTER,
				  image : that.cameraUrl,
				  scale : 0.25
				});
			billboard.isCamera = true;
			cameraFrustum.bb = billboard;
			
			console.log("Attempting to add frustum: " + 
					cameraFrustum.f1.lon + " , " + cameraFrustum.f1.lat  + " , " + cameraFrustum.f1.h  + " - " +
					cameraFrustum.f2.lon + " , " + cameraFrustum.f2.lat  + " , " + cameraFrustum.f2.h  + " - " +
					cameraFrustum.f3.lon + " , " + cameraFrustum.f3.lat  + " , " + cameraFrustum.f3.h  + " - " +
					cameraFrustum.f4.lon + " , " + cameraFrustum.f4.lat  + " , " + cameraFrustum.f4.h  + "."
					);
			
			 that.cameraFrustrumPolylines.add({
			        positions : Cesium.Cartesian3.fromDegreesArrayHeights([
			            cameraFrustum.f1.lon, cameraFrustum.f1.lat, cameraFrustum.f1.h,
			            cameraFrustum.f2.lon, cameraFrustum.f2.lat, cameraFrustum.f2.h,
			            cameraFrustum.f3.lon, cameraFrustum.f3.lat, cameraFrustum.f3.h,
			            cameraFrustum.f4.lon, cameraFrustum.f4.lat, cameraFrustum.f4.h,
			        ]),
			        width : 3.0,
			        loop : true
			    });		
			 
			 that.cameraFrustrumPolylines.add({
			        positions : Cesium.Cartesian3.fromDegreesArrayHeights([
			            cameraFrustum.cameraLoc.lon, cameraFrustum.cameraLoc.lat, cameraFrustum.cameraLoc.h,
			            cameraFrustum.f1.lon, cameraFrustum.f1.lat, cameraFrustum.f1.h,
			        ]),
					 material : Cesium.Material.fromType('Color', {
				            color : that.frustumColor
				        }),					
			        width : 1.0,
			    });		
			
			 that.cameraFrustrumPolylines.add({
			        positions : Cesium.Cartesian3.fromDegreesArrayHeights([
			            cameraFrustum.cameraLoc.lon, cameraFrustum.cameraLoc.lat, cameraFrustum.cameraLoc.h,
			            cameraFrustum.f2.lon, cameraFrustum.f2.lat, cameraFrustum.f2.h,
			        ]),
					 material : Cesium.Material.fromType('Color', {
				            color : that.frustumColor
				        }),					
			        width : 1.0,
			    });		
			 
			 that.cameraFrustrumPolylines.add({
			        positions : Cesium.Cartesian3.fromDegreesArrayHeights([
			            cameraFrustum.cameraLoc.lon, cameraFrustum.cameraLoc.lat, cameraFrustum.cameraLoc.h,
			            cameraFrustum.f3.lon, cameraFrustum.f3.lat, cameraFrustum.f3.h,
			        ]),
					 material : Cesium.Material.fromType('Color', {
				            color : that.frustumColor
				        }),					
			        width : 1.0,
			    });		
			 
			 that.cameraFrustrumPolylines.add({
			        positions : Cesium.Cartesian3.fromDegreesArrayHeights([
			            cameraFrustum.cameraLoc.lon, cameraFrustum.cameraLoc.lat, cameraFrustum.cameraLoc.h,
			            cameraFrustum.f4.lon, cameraFrustum.f4.lat, cameraFrustum.f4.h,
			        ]),
					 material : Cesium.Material.fromType('Color', {
				            color : that.frustumColor
				        }),					
			        width : 1.0,
			    });		
			 
			that.cameraFrustums.push(cameraFrustum);
		},
		error : function() {
			console.log("Could not fetch camera frustum");
		},
		dataType : 'json'
	});	
}


MapViewer.prototype.addCameraRay = function(img) {	
	//var items = document.getElementById('historySelection');
	//var selectedHistory = parseInt(items.options[items.selectedIndex].value);
	var that = this;
	console.log("Fetching camera ray " +  img.id);

	$.ajax({
		type : "GET",
		url : "/apps/tiepoint/fetchCameraRay",
		data : {
			imageId : img.id,
//			history : selectedHistory
		},
		success : function(data) {
			console.log("Retrieved camera ray for image "
					+ img.id);
			if (mainViewer.displayCounter != img.displayCounter) {
				console.log("Image camera out of date, ignoring result..." + img.id);
				return;
			}
			
			var ray = {};
			ray.start = { lat : data.lat[0], lon : data.lon[0], h : data.h[0] };
			ray.end = { lat : data.lat[1], lon : data.lon[1], h : data.h[1] };
			
			console.log("Attempting to add ray: " + 
					ray.start.lon + " , " + ray.start.lat  + " , " + ray.start.h  + " - " +
					ray.end.lon + " , " + ray.end.lat  + " , " + ray.end.h  + "."
			);
			
			var polyline = that.cameraFrustrumPolylines.add({
			        positions : Cesium.Cartesian3.fromDegreesArrayHeights([
			            ray.start.lon, ray.start.lat, ray.start.h,
			            ray.end.lon, ray.end.lat, ray.end.h
			        ]),
			        
			        material : Cesium.Material.fromType('Color', {
			            color : that.frustumColor
			        }),
			        
			        width : 1.0
			    });	
		},
		error : function() {
			console.log("Could not fetch camera ray");
		},
		dataType : 'json'
	});	
}

MapViewer.prototype.addTiePointRay = function(img, tiePoint) {	
	//var items = document.getElementById('historySelection');
	//var selectedHistory = parseInt(items.options[items.selectedIndex].value);
	var that = this;
	var point = tiePoint.fields.point.coordinates;
	console.log("Fetching camera ray " +  img.id + " - x " + point[0] + " y " + point[1]);

	$.ajax({
		type : "GET",
		url : "/apps/tiepoint/fetchCameraRay",
		data : {
			imageId : img.id,
			X : Math.round(point[0]),
			Y : Math.round(point[1]),
//			history : selectedHistory
		},
		success : function(data) {
			console.log("Retrieved camera ray for image "
					+ img.id);
			if (mainViewer.displayCounter != img.displayCounter) {
				console.log("Image camera out of date, ignoring result..." + img.id);
				return;
			}
			
			var ray = {};
			ray.start = { lat : data.lat[0], lon : data.lon[0], h : data.h[0] };
			ray.end = { lat : data.lat[1], lon : data.lon[1], h : data.h[1] };
			
			console.log("Attempting to add ray: " + 
					ray.start.lon + " , " + ray.start.lat  + " , " + ray.start.h  + " - " +
					ray.end.lon + " , " + ray.end.lat  + " , " + ray.end.h  + "."
			);
			
			var polyline = null;
			if (that.selectedCtrlPt.id == tiePoint.fields.geoPoint) {
				polyline = that.tiePointPolylines.add({
			        positions : Cesium.Cartesian3.fromDegreesArrayHeights([
			            ray.start.lon, ray.start.lat, ray.start.h,
			            ray.end.lon, ray.end.lat, ray.end.h
			        ]),
			        
			        material : Cesium.Material.fromType('Color', {
			            color : that.activeRayColor
			        }),
			        
			        width : 2.0
			    });	
				if (that.lastSelectedTiePoints == null) {
					that.lastSelectedTiePoints = {};
				}
				that.lastSelectedTiePoints[img.id] = polyline;
			} else {
				polyline = that.tiePointPolylines.add({
			        positions : Cesium.Cartesian3.fromDegreesArrayHeights([
			            ray.start.lon, ray.start.lat, ray.start.h,
			            ray.end.lon, ray.end.lat, ray.end.h
			        ]),
			        
			        material : Cesium.Material.fromType('Color', {
			            color : that.inactiveRayColor
			        }),
			        
			        width : 2.0
			    });	
			}
			
			var raysForImg = that.tiePointRays[img.id];
			if (raysForImg == null) {
				that.tiePointRays[img.id] = {};
				raysForImg = that.tiePointRays[img.id];
			}
			raysForImg[tiePoint.fields.geoPoint] = polyline;
		},
		error : function() {
			console.log("Could not fetch camera ray");
		},
		dataType : 'json'
	});	
}

MapViewer.prototype.removeTiePointRay = function(img, line) {
	var selected = this.lastSelectedTiePoints[img.id];
	if (selected) {
		delete this.lastSelectedTiePoints[img.id];
	}
	this.tiePointPolylines.remove(line);
}

MapViewer.prototype.clearImageData = function() {	
	console.log("clearing image data");
	this.cameraBillboards.removeAll();
	this.cameraFrustrumPolylines.removeAll();
	this.tiePointPolylines.removeAll();
	console.log("TiePointPolylines = " + this.tiePointPolylines.length);
	this.cameraFrustums = [];
	this.tiePointRays = {};
	this.lastSelectedTiePoints = null;
}

MapViewer.prototype.setActiveControlPoint = function(controlPoint) {
	var that = this;
	that.selectedCtrlPt = controlPoint;
	if (that.lastSelected != null) {
		that.lastSelected.image = that.inactiveCtrlPointUrl	
	}
	if (controlPoint != null) {
		console.log("Selecting control point in map " + controlPoint.name + ". " + controlPoint.id);
		var data = this.controlPointRefs[controlPoint.id];
		if (data) {
			that.lastSelected = data.bb;
			that.lastSelected.image = that.activeCtrlPointUrl
		}
	} 
	
	if (that.lastSelectedTiePoints) {
		for (var i in that.lastSelectedTiePoints) {
			var line = that.lastSelectedTiePoints[i];
			line.material = Cesium.Material.fromType('Color', {
	            color : that.inactiveRayColor
	        })
		}
	}
	
	that.lastSelectedTiePoints = {};
	for (var id in that.tiePointRays) {
		var raysForImg = that.tiePointRays[id];
		if (raysForImg != null) {
			var line = raysForImg[controlPoint.id];
			if (line != null) {
				console.log("Selecting polyline for control point id " + controlPoint.id);
				that.lastSelectedTiePoints[id] = line; // store the last selected id by image id
				line.material = Cesium.Material.fromType('Color', {
		            color : that.activeRayColor
		        })				
			}
		}
	}
}

MapViewer.prototype.handleTiePointUpdate = function(img, tiePoint) {
	console.log("Updating tie point " + tiePoint.fields.geoPoint);
	var raysForImg = this.tiePointRays[img.id];
	if (raysForImg == null) {
		this.addTiePointRay(img, tiePoint);
	} else {
		var line = raysForImg[tiePoint.fields.geoPoint];
		if (line != null) {
			this.removeTiePointRay(img, line);
			this.addTiePointRay(img, tiePoint);					
		}
	}
}

MapViewer.prototype.toggleTiePoint = function(img, tiePoint, show) {
	console.log("Toggling tie point " + tiePoint.fields.geoPoint);
	var raysForImg = this.tiePointRays[img.id];
	if (raysForImg == null) {
		if (show) {
			this.addTiePointRay(img, tiePoint);
		} // else ignore it, it doesn't get drawn.
	} else {
		var line = raysForImg[tiePoint.fields.geoPoint];
		if (line != null) {
			this.removeTiePointRay(img, line);
		}
		
		if (show) {
			this.addTiePointRay(img, tiePoint);
		} else {
			delete raysForImg[tiePoint.fields.geoPoint];
		}
	}
}

MapViewer.prototype.updateAvailableControlPoint = function(controlPoint) {
	if (controlPoint != null) {
		if (controlPoint.isInActiveSet) {
			this.addControlPoint(controlPoint);
		}
		else {
			this.removeControlPoint(controlPoint);
		}
	}
}