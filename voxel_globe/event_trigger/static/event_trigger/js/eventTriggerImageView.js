/*
 * The Tie point editor is the main class for an individual OL3 imageviewer
 */

function EventTriggerEditor(app, imageContainerDivName, editorCount) {
	this.app = app;
	this.planetDivName = "planetWrapper" + editorCount;
	this.divName = "imageWrapper" + editorCount;
	this.toolbarDivName = "imageToolbar" + editorCount;
	this.imageDivName = "image" + editorCount;
	this.imageNameField = "imageName" + editorCount;

	this.drawShapeButton = "drawShapeBtn" + editorCount;
	this.removeButton = "removeBtn" + editorCount;
	this.saveButton = "saveBtn" + editorCount;

	this.editorId = editorCount;
	this.imageEditor = null;
	this.img = null;
	this.map = null;
	this.isInitializing = false;

	var divText = '<div id="' + this.planetDivName + '" class="planetWidget">' +
			'<div id="' + this.divName + '" class="imageWidget"><div id="' + this.imageDivName
			+ '" class="imageContents"></div><div id="' + this.toolbarDivName
			+ '" class="imageToolbar"></div></div>';
	$('#' + imageContainerDivName).append(divText);

	this.editorState = {
		shape : []
	};
	
	console.log("STARTUP: Banner height " + this.bannerHeight + " image height " + this.imageHeight);
}

EventTriggerEditor.prototype.initialize = function(selectedImageSet, img, selectedSite, selectedCameraSet) {
	if (this.isInitialzing) {
		return;
	}
	this.editorState.selectedImageSet = selectedImageSet;
	this.editorState.selectedSite = selectedSite
	this.editorState.imageId = img.id;
	this.isInitializing = true;
	console.log("Initializing image " + img.name + " id " + img.id + " selectedImageSet " + selectedImageSet);

	$('#' + this.divName).css("height", this.imageHeight + "px");
	$('#' + this.imageDivName).html("");
	$('#' + this.toolbarDivName).html("");
	$('#' + this.toolbarDivName).toggle(true);
	$('#' + this.bannerDivName).toggle(true);
	$('#' + this.planetDivName).toggle(true);

	this.imageEditor = new ImageViewer(this.imageDivName, img, selectedCameraSet);
	this.img = img;
	this.map = this.imageEditor.map;
	this.imgName = img.name;
	var crossOrigin = 'anonymous';
	var that = this;
	this.selectedFeature = null;

	//a vector of features, start with no features
	this.drawsource = new ol.source.Vector();

  //Styles for tie points
	var inactiveStyle = new ol.style.Style({
		image : new ol.style.Circle({
			radius : 5,
			stroke : new ol.style.Stroke({
				color : INACTIVE_COLOR,
				width : 2
			}),
		}),
		fill: new ol.style.Fill({
            color: 'rgba(255, 255, 255, 0.2)'
        }),
		stroke : new ol.style.Stroke({
			color : INACTIVE_COLOR,
			width : 2
		}),
	});
	var activeStyle = new ol.style.Style({
		image : new ol.style.Circle({
			radius : 5,
			stroke : new ol.style.Stroke({
				color : ACTIVE_COLOR,
				width : 2
			})
		}),
		fill: new ol.style.Fill({
            color: 'rgba(255, 255, 255, 0.2)'
        }),
		stroke : new ol.style.Stroke({
			color : ACTIVE_COLOR,
			width : 2
		}),
	});
	
	//Creates the actual layer to get rendered, for tiled images
	var vector = new ol.layer.Vector({
		source : that.drawsource,
		style : inactiveStyle
	});

  //This seems to handle events on the entire map, not just a feature?
	this.select = new ol.interaction.Select({
		// condition : ol.events.condition.singleClick,
		// addCondition : ol.events.condition.singleClick,
		// removeCondition : ol.events.condition.never,
		// toggleCondition : ol.events.condition.singleClick,
		style : activeStyle
	});

	//This is triggered when an inactive point is clicked.
  //This is one way the active control point is changed.
	this.select.on('select', function (e) {
		// get the feature
		var feature = e.selected[0];
		that.selectedFeature = feature;
	}); 

	this.modify = new ol.interaction.Modify({
		features : that.select.getFeatures(),
		style : activeStyle
	});

	this.modify.on('modifyend', function(e) {	
		//mainViewer.completeEdit();
		console.log("Finished modifying...");
		that.saveShape(false);
	});

	var interactions = this.map.getInteractions();
	interactions.extend([that.select, that.modify]);
	this.map.addLayer(vector);

	//I have NO clue what I'm doing here https://groups.google.com/forum/#!topic/ol3-dev/SEu5Js8OurU
  this.map.renderSync();
  //If I don't do this, coordinate will turn up null deep in ol because the mapping of
  //pixels to coordinates is not yet initialized. This then breaks a lot of code
  //By renderSync here, the pixel conversion code works and everything is happy.

   //This is used when adding a new point
	var drawingTool = new ol.interaction.Draw({
		source : that.drawsource,
		type : "Polygon" // can also be LineString, Polygon someday
	}); // global so we can remove it later


	drawingTool.on('drawend', function(e) {
		// temporarily disable double-click zoom
		controlDoubleClickZoom(false);

		console.log("Drawing ended");
		// make the drawn feature a candidate for
		// modification
		// that.currentAction = null;
		that.selectedFeature = e.feature;
		// e.feature.controlPoint = that.activeControlPoint;
		// that.editorState[that.activeControlPoint.id] = {
		// 	feature : e.feature
		// };
		that.map.removeInteraction(drawingTool);
		//that.select.getFeatures().clear();
		that.map.addInteraction(that.select);
		//that.select.getFeatures().push(e.feature); // Make sure it continues to
		// 											// be selected
		// $('#' + that.addButton).prop("disabled", "disabled");
		// $('#' + that.removeButton).prop("disabled", "");
		// that.createTiePointFromFeature(e.feature);
		// mainViewer.startTiePointEdit(that, e.feature.controlPoint);
		//		});
		that.saveShape(true);
		$('#' + that.drawShapeButton).prop("disabled", "");

		// re-initialize double click zoom after short delay
		setTimeout(function(){controlDoubleClickZoom(true);},251); 
	});

	//Control active state of double click zoom interaction
	// as per https://github.com/openlayers/ol3/issues/3610
	function controlDoubleClickZoom(active){
	    var interactions = that.map.getInteractions();
	    for (var i = 0; i < interactions.getLength(); i++) {
	        var interaction = interactions.item(i);                          
	        if (interaction instanceof ol.interaction.DoubleClickZoom) {
	            interaction.setActive(active);
	        }
	    }
	}

  var that = this;

  // Set up the image editor toolbar buttons
	// $('#' + this.toolbarDivName).append(
	// 			'<button id="' + this.saveButton + '"><img height=12 src="' + iconFolderUrl + "plus.png" +'" style="vertical-align:middle;"></img></button>');
	// $('#' + this.saveButton)
	// 		.click(
	// 				function(e) {
	// 					console.log("save shape");
	// 					that.currentAction = "saveShape";
						
	// 					$('#' + that.saveButton).toggle(false);
	// 					$('#' + that.drawShapeButton).toggle(true);
	// 				});
	$('#' + this.toolbarDivName).append(
				'<button id="' + this.drawShapeButton + '"><img height=12 src="' + iconFolderUrl + "plus.png" +'" style="vertical-align:middle;"></img></button>');
	$('#' + this.drawShapeButton)
			.css('margin', '10px 5px')
			.click(
					function(e) {
						console.log("start drawing shape");
						that.currentAction = "drawShape";
						$('#' + that.drawShapeButton).prop("disabled", "disabled");
						that.map.removeInteraction(that.select);
						that.map.addInteraction(drawingTool);
					})

	// $('#' + this.toolbarDivName).append(
	// 		'<button id="' + this.drawHeightButton + '">Draw Height</button>');
	// $('#' + this.drawHeightButton)
	// 		.css('margin', '5px')
	// 		.click(
	// 				function(e) {
	// 					console.log("start drawing height");
	// 					that.currentAction = "drawHeight";
	// 				})

	// $('#' + this.toolbarDivName).append(
	// 		'<button id="' + this.removeButton + '">Clear Drawing</button>');
	// $('#' + this.removeButton)
	// 		.css('margin', '5px')
	// 		.click(
	// 				function(e) {
	// 					console.log("Clear");
	// 					that.currentAction = "clear";
	// 					that.drawsource.clear();
	// 					$('#' + that.saveButton).toggle(false);
	// 					$('#' + that.drawShapeButton).toggle(true);
	// 				})
	$("button").button();
}

EventTriggerEditor.prototype.blank = function() {
	this.img = null;
	this.isInitializing = false;
	$('#' + this.imageDivName).html("");
	$('#' + this.toolbarDivName).toggle(false);
	$('#' + this.planetDivName).toggle(false);
}

EventTriggerEditor.prototype.show = function(width, height, scale) {
	$('#' + this.planetDivName).css("height", '100%');
	$('#' + this.planetDivName).css("width", width + '%');
	$('#' + this.bannerDivName).css("font-size", scale + '%');
	$('#' + this.planetDivName).toggle(true);
}

EventTriggerEditor.prototype.hide = function() {
	$('#' + this.planetDivName).toggle(false);
	this.blank();
}

// EventTriggerEditor.prototype.initializeContainerSize = function() {		
// 	$('#' + this.bannerDivName).html('<img src="' + iconFolderUrl + 'planet.svg">' + 
// 		'<div class="p1">Includes material ©2016 Planet Labs Inc. All rights reserved.</div>' +
// 		'<div class="p2">DISTRIBUTION STATEMENT C: Distribution authorized to U.S. Government Agencies and their contractors (Administrative or Operational Use) Other requests for this document shall be referred to AFRL/RYAA, Wright-Patterson Air Force Base, OH 45433-7321.</div>');

// 	var bheight = document.getElementById(this.bannerDivName).clientHeight;
// 	if (bheight > 0) {
// 		this.bannerHeight = bheight;
// 	}

// 	var cheight = $('#editorContentDiv').height();
// 	this.imageHeight = cheight - this.bannerHeight;
// }

EventTriggerEditor.prototype.saveShape = function(creating) {
	console.log("Saving shape...");
	var feature = this.selectedFeature;
	var points = feature.getGeometry().getCoordinates();
	shape = points[0];

	var shapeString = "";
	for (var i = 0; i < shape.length; i++) {
		var pt = shape[i];
		pt[1] = -1 * pt[1];
		shapeString += pt[0] + "," + pt[1];
		if (i < shape.length - 1) {
			shapeString += ",";
		}
	}

	if (creating) {
		this.app.createEventTriggerRegion(this.editorState.imageId, shapeString);
	} else {
		this.app.editEventTriggerRegion(0, shapeString); // TODO get region ID and pass it in
	}
}

EventTriggerEditor.prototype.getDebugInfo = function() {
	if (this.drawsource) {
		var farray = this.drawsource.getFeatures();
		var text = this.divName + '<br>';
		for (var i = 0; i < farray.length; i++) {
			var points = farray[i].getGeometry().getCoordinates();
			text += "POLY " + points + '<br>';
		}
		return text;
	} else {
		return this.divName + ' has no drawn features.<br>';
	}

	if (this.map) {
		var center = this.map.getView().getCenter();
		var zoom = this.map.getView().getZoom();
		
		return "Center - " + center + " Zoom - "+ this.map.getView().getZoom() + "<br>";
	} else {
		return "No image displayed.<br>";
	}
}

