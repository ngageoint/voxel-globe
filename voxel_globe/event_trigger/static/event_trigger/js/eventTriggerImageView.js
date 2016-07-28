function EventTriggerEditor(imageContainerDivName, editorCount) {
	this.planetDivName = "planetWrapper" + editorCount;
	this.divName = "imageWrapper" + editorCount;
	this.toolbarDivName = "imageToolbar" + editorCount;
	this.imageDivName = "image" + editorCount;
	this.imageNameField = "imageName" + editorCount;

	this.drawShapeButton = "drawShapeBtn" + editorCount;
	this.drawHeightSpinner = "drawHeightSpinner" + editorCount;
	this.removeButton = "removeBtn" + editorCount;
	this.saveButton = "saveBtn" + editorCount;

	this.editorId = editorCount;
	this.img = null;
	this.isInitializing = false;

	var divText = '<div id="' + this.planetDivName + '" class="planetWidget">' +
			'<div id="' + this.divName + '" class="imageWidget"><div id="' + this.imageDivName
			+ '" class="imageContents"></div><div id="' + this.toolbarDivName
			+ '" class="imageToolbar"></div></div>';
	$('#' + imageContainerDivName).append(divText);

	this.editorState = {
		shape : [],
		shapeHeight : 10,
	};
	
	console.log("STARTUP: Banner height " + this.bannerHeight + " image height " + this.imageHeight);
}

EventTriggerEditor.prototype.initialize = function(selectedImageSet, img, selectedSite) {
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

	this.imageEditor = new ImageViewer(this.imageDivName, img);
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

	this.modify = new ol.interaction.Modify({
		features : that.select.getFeatures(),
		style : activeStyle
	});

	this.modify.on('modifyend', function(e) {	
		//mainViewer.completeEdit();
		console.log("Finished modifying...");
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
		// that.selectedFeature = e.feature;
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
		
		$('#' + that.drawShapeButton).toggle(false);
		$('#' + that.saveButton).toggle(true);

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
  	$('#' + this.toolbarDivName).append(
			'<button id="' + this.saveButton + '" style="display:none">Save Shape</button>');
	$('#' + this.saveButton)
			.click(
					function(e) {
						console.log("save shape");
						that.currentAction = "saveShape";
						var saveName = prompt("Save shape as: ");
						that.saveShape(saveName);
					});
	$('#' + this.toolbarDivName).append(
			'<button id="' + this.drawShapeButton + '">Draw Shape</button>');
	$('#' + this.drawShapeButton)
			.css('margin', '10px 5px')
			.click(
					function(e) {
						console.log("start drawing shape");
						that.currentAction = "drawShape";
						that.map.removeInteraction(that.select);
						that.map.addInteraction(drawingTool);
					})
	$('#' + this.toolbarDivName).append(
			'<label for="' + this.drawHeightSpinner + '">Shape Height (in meters): </label><input id="' + this.drawHeightSpinner + '" value="' + this.editorState.shapeHeight + '"" size=4 max=9999 min=0 style="height:16px; width:40px;" type=number disabled></input>');
	$('#' + this.drawHeightSpinner).change(function() {
		var val = $('#' + that.drawHeightSpinner).val();
		if (!$.isNumeric(val) || val < 0 || val > 9999) {
			alert("Height must be between 0 and 9999 meters.");
			$('#' + that.drawHeightSpinner).val(that.editorState.shapeHeight);
		} else {
			that.editorState.shapeHeight = console.log("Height value is " + val);
		}
	});

	$('#' + this.toolbarDivName).append(
			'<button id="' + this.removeButton + '">Clear Drawing</button>');
	$('#' + this.removeButton)
			.css('margin', '5px')
			.click(
					function(e) {
						console.log("Clear");
						that.currentAction = "clear";

						that.drawsource.clear();
						$('#' + that.saveButton).toggle(false);
						$('#' + that.drawShapeButton).toggle(true);
					})
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
}

EventTriggerEditor.prototype.saveShape = function(name) {
	console.log("Saving shape as " + name);
	if (this.drawsource) {
		var farray = this.drawsource.getFeatures();
		for (var i = 0; i < farray.length; i++) { // should only be 1 feature for now - a single shape
			var points = farray[i].getGeometry().getCoordinates();
			this.editorState.shape = points[0];
		}

		this.editorState.shapeString = "";
		for (var i = 0; i < this.editorState.shape.length; i++) {
			var pt = this.editorState.shape[i];
			pt[1] = -1 * pt[1];
			this.editorState.shapeString += pt[0] + "," + pt[1];
			if (i < this.editorState.shape.length - 1) {
				this.editorState.shapeString += ",";
			}
		}
	}

	this.editorState.saveName = name;

	console.log("Saving shape: " + this.editorState.shape);
	var that = this;

	// ANDY HERE...
	$.ajax({
		type : "POST",
		url : "/apps/event_trigger/create_event_trigger",
		data : {
			name : that.editorState.saveName,
			image_id : that.editorState.imageId, 
			site_id : that.editorState.selectedSite,
			image_set_id : that.editorState.selectedImageSet,
			points : that.editorState.shapeString
		},
		success : function(data) {
			console.log("Event Trigger Saved");
		},
		error : function() {
			alert("Unable to save event trigger");
		},
		dataType : 'html'
	});
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

