var timeout;
var ACTIVE_COLOR = 'rgba(255, 255, 0, 0.9)';
var INACTIVE_COLOR = 'rgba(119, 204, 255, 0.75)';

/**
 * This class supports the overall UI layout and data.
 */
function TiePointMain() {
	this.imageEditors = [];
	this.mapViewer = null;
	this.videos = [];
	this.images = [];
	this.controlPoints = {};
	this.numImagesToDisplay = 1;
	this.displayingImage = 0;
	this.selectedVideo = -1;
	this.imageWidths = [ 99, 49, 32, 24, 24, 24, 24, 24 ];
	this.imageHeights = [ 99, 99, 99, 99, 49, 49, 49, 49 ];
	this.imagePaginator;
	this.controlPointOptions;
	this.configurationAction = null;
	
	this.activeImageEditor = null;
	this.editedControlPoint = null;
	this.displayCounter = 0;
	this.visibleImageCounter = 0;
	this.initializedImageCounter = 0;
}

TiePointMain.prototype.updateLayout = function() {
	this.numImagesToDisplay = parseInt($.trim($('#numImagesPerPage').val()));
	console.log("Number of images to display " + this.numImagesToDisplay);
	for (var i = 0; i < this.imageEditors.length; i++) {
		this.imageEditors[i].hide();
	}
	var width = this.imageWidths[this.numImagesToDisplay - 1];
	var height = this.imageHeights[this.numImagesToDisplay - 1];

	for (var i = 0; i < this.numImagesToDisplay; i++) {
		this.imageEditors[i].show(width, height);
	}
	this.imagePaginator.initialize(this.images.length, this.numImagesToDisplay, this.displayingImage, displayImage);
};

TiePointMain.prototype.displayImage = function(imgNdx) {
	console.log("Displaying image " + imgNdx);
	$('#selectImgControlPoints').prop("disabled","disabled"); // disable it until control points are loaded
	this.displayCounter++;

	var that = this;
	this.displayingImage = imgNdx;
	this.mapViewer.clearImageData();
	var j = imgNdx;
	this.visibleImageCounter = 0;
	this.initializedImageCounter = 0;
	for (var i = 0; i < this.numImagesToDisplay; i++) {
		var imgEditor = this.imageEditors[i];
		var img = this.images[j];
		if (img) {
			var that = this;
			this.visibleImageCounter++;
			// load existing tie points into the editor state and create features for them someday...
			img.displayCounter = this.displayCounter;
			imgEditor.initialize(img, that.controlPoints);			
			this.mapViewer.addCamera(img);
			this.mapViewer.addCameraRay(img);
		} else {
			imgEditor.blank();
		}
		j++;
	}
	this.controlPointOptions.refreshSelection();
};

TiePointMain.prototype.incrementImageInitialized = function() {
	this.initializedImageCounter++;	
	if (this.initializedImageCounter == this.visibleImageCounter) {
		this.updateWhenAllImagesInitialized();
	}
}

/**
 * Called when all image viewers have finished pulling their data and initializing completely.
 */
TiePointMain.prototype.updateWhenAllImagesInitialized = function() {
	$('#selectImgControlPoints').prop("disabled", null); // enable option to select all control points based on img tie points
	
	// ANDY, your code for updating the editors about the selected point should go here....
	for (var i = 0; i < this.numImagesToDisplay; i++) {
		var imgEditor = this.imageEditors[i];
		if ($('#zoomTiePoint').prop("checked") && 
			(imgEditor.activeControlPoint != null) && 
			(imgEditor.activeControlPoint.id in imgEditor.editorState)) {
		  	imgEditor.map.getView().setZoom(parseInt($.trim($('#zoomTiePointLevel').val())));
		  	imgEditor.map.getView().setCenter([ imgEditor.editorState[imgEditor.activeControlPoint.id].tiePoint.fields.point.coordinates[0], 
		  	                                   -imgEditor.editorState[imgEditor.activeControlPoint.id].tiePoint.fields.point.coordinates[1] ]) // width, -height
		}
	}

}

TiePointMain.prototype.initializeMap = function(mapConfig) {
	this.mapViewer = new MapViewer();
	this.mapViewer.initialize(mapConfig);
};

TiePointMain.prototype.showHideMapDisplay = function() {
	console.log("Changing map display");
	if ($('#showMap').prop("checked")) {
		$('#sideBuffer').toggle(false);
		$('#imageContainer').css("width", "61%");
		$('#mapContainer').toggle(true);
	} else {
		$('#mapContainer').toggle(false);
		$('#sideBuffer').toggle(true);
		$('#imageContainer').css("width", "95%");
	}
	this.displayImage(this.displayingImage);
};

TiePointMain.prototype.chooseVideoToDisplay = function(videoNdx) {
	console.log("Loading video " + this.videos[videoNdx].id);
	for (var i = 0; i < this.videos.length; i++) {
		if (videoNdx != i) {
			$('#videoList' + i).prop("checked", "");
		}
	}
	this.images = [];
	var that = this;
	$.ajax({
		type : "GET",
		url : "/meta/rest/auto/image",
		data : {
			imagecollection : that.videos[videoNdx].id
		},
		success : function(data) {
			// Toggle all other image selection buttons
			if (data.error) {
				alert(data.error);
			} else {				
				for (var i = 0; i < data.length; i++) {
					var img = {
						id : data[i].id,
						name : data[i].name,
						url : data[i].imageUrl,
						width : data[i].imageWidth,
						height : data[i].imageHeight
					};
					that.images.push(img);
				}
				if (that.images.length > 0) {
					that.imagePaginator.initialize(that.images.length, that.numImagesToDisplay, 0, displayImage);
					//that.displayImage(0);
				} else {
					$('#imageWidget').html("No images found in the database.");
				}
			}
		},
		dataType : 'json'
	});

};

TiePointMain.prototype.toggleControlPoint = function(controlPointId) {
	console.log("Toggling control point " + controlPointId);
	var isChecked = $('#pointList' + controlPointId).prop("checked");
	this.controlPoints[controlPointId].isInActiveSet = isChecked;
	
	// Update options...
	this.controlPointOptions.togglePoint(controlPointId);	

	for (var i = 0; i < this.numImagesToDisplay; i++) {
		var imgEditor = this.imageEditors[i];
		imgEditor.updateAvailableControlPoint(this.controlPoints[controlPointId]);
	}
	
	this.mapViewer.updateAvailableControlPoint(this.controlPoints[controlPointId]);

	// Update options...
	this.controlPointOptions.updateSelectionForToggle(controlPointId);	

};

TiePointMain.prototype.initializeVideoSelector = function() {
	$('#videoList').html("");
	for (var i = 0; i < this.videos.length; i++) {
		$('#videoList').append(
				'<input id="videoList' + i + '" onclick="mainViewer.chooseVideoToDisplay('
						+ i + ')" type="radio"></input> ' + this.videos[i].name
						+ '</br>');
	}
};

TiePointMain.prototype.initializeControlPointSelector = function() {
	$('#controlPointList').html("");
	var i = 0;
	for (var id in this.controlPoints) {
		if (this.controlPoints[id].isInActiveSet) {
			$('#controlPointList').append(
					'<input id="pointList' + id + '" type="checkbox" onchange="mainViewer.toggleControlPoint('
					+ id + ')" checked></input>'
							+ this.controlPoints[id].name + '</br>');			
		} else {
			$('#controlPointList').append(
					'<input id="pointList' + id + '" type="checkbox" onchange="mainViewer.toggleControlPoint('
					+ id + ')"></input>'
							+ this.controlPoints[id].name + '</br>');
		}
		i++;
	}
	
	this.controlPointOptions.initialize(this.controlPoints, null, handleControlPointSelection, handleImageFiltering);
};

TiePointMain.prototype.pullDataAndUpdate = function() {
	var that = this;
	$.ajax({
		type : "GET",
		url : "/meta/rest/auto/imagecollection",
		data : {},
		success : function(data) {
			for (var i = 0; i < data.length; i++) {
				var img = {
					id : data[i].id,
					name : data[i].name
				};
				that.videos.push(img);
			}
			if (that.videos.length > 0) {
				that.initializeVideoSelector();
			} else {
				$('#imageWidget').html("No images found in the database.");
			}
		},
		dataType : 'json'
	});

	$.ajax({
		type : "GET",
		url : "/meta/rest/auto/controlpoint",
		data : {},
		success : function(data) {
			// alert("received json data...http://" + window.location.host +
			// data[0].imageUrl);
			for (var i = 0; i < data.length; i++) {
				var geoPt = {
					id : data[i].id,
					name : data[i].name,
					isInActiveSet : false,
					lat : data[i].point.coordinates[1],
					lon : data[i].point.coordinates[0],
					alt : data[i].point.coordinates[2]
				};
				$('#controlPointList').append(
						'<li>' + data[i].name + '</li>');
				that.controlPoints[geoPt.id] = geoPt;
			}
			if (data.length == 0) {
				$('#controlPointList').html(
						"No geographic control points found in the database.");
			} else {
				that.initializeControlPointSelector();
			}
		},
		dataType : 'json'
	});
};

TiePointMain.prototype.initializeDataAndEvents = function() {

	this.initializeMap({useSTKTerrain: true});
	// TODO: Figure out how to get initial region for the map
	this.mapViewer.setHomeLocation(40.423256522222, -86.913520311111, 1000);

	for (var i = 0; i < 8; i++) {
		var imgEditor = new TiePointEditor("imageContainer", i);
		this.imageEditors.push(imgEditor);
	}
	this.imagePaginator = new Paginator({div : "paginator", id : "1"});
	this.controlPointOptions = new ControlPointOptions( {div : "controlPointOptions", id : "1"});
	
	// wire in dynamic layout and page
	this.updateLayout();

	// Set up the initial state
	this.showHideMapDisplay(); // make map display consistent with checkbox
	var that = this;
	$('#editorContentDiv').css("height", $(window).height() - 140 + "px");
	$('#editorContentDiv').css("width", $(window).width() - 20 + "px");
	$(window).resize(function(e) {
		$('#editorContentDiv').css("height", $(window).height() - 140 + "px");
		$('#editorContentDiv').css("width",  $(window).width() - 20 + "px");
		clearTimeout(timeout);
		timeout = setTimeout(refreshDisplay, 300);
	});

	// Start by choosing a video
	this.imagePaginator.initialize(0, this.numImagesToDisplay, this.displayingImage, new function() {});

	$('#selectImgControlPoints').prop("disabled","disabled"); // disable it until control points are loaded
	$('#videoSelectionOptions').toggle(true);
	$('#controlPointSelectionOptions').toggle(false);
	$('#sideControlsContentDiv').toggle(true);
	this.activeSelector = "video";

	$('#videoList').html("Downloading video list...");
	$('#controlPointList').html("Downloading control point list...");

	// Set up all of the events...
	$('#numImagesPerPage').change(function(e) {		
		var num = parseInt($.trim($('#numImagesPerPage').val()));
		if (num >= 1 && num <= 8) {
			that.updateLayout();
		} else {
			alert("The number of displayed images should be between 1 and 8");
		}
	});

	$('#videoSelectorDiv').mousedown(function(e) {
		console.log("Selecting video selector...");
		if (that.activeSelector == "video") {
			$('#sideControlsContentDiv').hide("slide", {}, 300);
			$('#videoSelectionOptions').toggle(false);
			$('#controlPointSelectionOptions').toggle(false);			
			that.activeSelector = null;
		} else {
			$('#controlPointSelectionOptions').toggle(false);
			$('#videoSelectionOptions').toggle(true);
			if (that.activeSelector == null) {
				$('#sideControlsContentDiv').show("slide", {}, 300);
			}
			that.activeSelector = "video";
		}
	});

	$('#controlPointSelectorDiv').mousedown(function(e) {
		console.log("Selecting control points...");
		if (that.activeSelector == "points") {
			$('#sideControlsContentDiv').hide("slide", {}, 300);
			$('#videoSelectionOptions').toggle(false);
			$('#controlPointSelectionOptions').toggle(false);			
			that.activeSelector = null;
		} else {
			$('#videoSelectionOptions').toggle(false);
			$('#controlPointSelectionOptions').toggle(true);
			if (that.activeSelector == null) {
				$('#sideControlsContentDiv').show("slide", {}, 300);
			}
			that.activeSelector = "points";
		}
	});

	$('#showMap').click(function(e) {
		that.showHideMapDisplay();
	});
	
	$('#zoomTiePoint').click(function(e) {
		that.displayImage(that.displayingImage);
	});

//	$('#historySelection').change(function(e) {
//		that.displayImage(that.displayingImage);
//	});

	$('#frustumSize').change(function(e) {
		that.displayImage(that.displayingImage);
	});

	$('#printDebugBtn').click(function(e) {
		var text = "Image Editor Point Contents<br>";
		for (var i = 0; i < that.imageEditors.length; i++) {
			text += that.imageEditors[i].getDebugInfo();
		}
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

//	$('#estimateCameraLocs').click(function (e) {
//		var items = document.getElementById('historySelection');
//		var selectedHistory = parseInt(items.options[items.selectedIndex].value);
//		console.log("Pressing the magic button, moving through history..." + selectedHistory);		
//		$('#historySelection option[value="' + selectedHistory + '"]').prop("selected", "false");
//		if (selectedHistory == 4) {
//			selectedHistory = 1;
//		} else {
//			selectedHistory += 1;
//		}
//		$('#historySelection').val(selectedHistory);
//		console.log("Pressing the magic button, moving through history..." + selectedHistory);
//		
//		that.displayImage(that.displayingImage);
//	})

	$('#clearSelectedControlPoints').click(function (e) {
		for (var id in that.controlPoints) {
			if (that.controlPoints[id].isInActiveSet) {
				$('#pointList' + id).prop("checked", "");
				that.toggleControlPoint(id);
			}
		}
	});
	
	$('#selectAllControlPoints').click(function (e) {
		for (var id in that.controlPoints) {
			if (!that.controlPoints[id].isInActiveSet) {
				$('#pointList' + id).prop("checked", "true");
				that.toggleControlPoint(id);
			}
		}
	});

	$('#selectImgControlPoints').click(function (e) {
		var keys = {};
		for (var i = 0; i < that.numImagesToDisplay; i++) {
			var imgEditor = that.imageEditors[i];
			if (imgEditor.img != null) {
				imgEditor.markImageControlPointIds(keys);
			}
		}
		for (var id in keys) {
			if (!that.controlPoints[id].isInActiveSet) {
				$('#pointList' + id).prop("checked", "true");
				that.toggleControlPoint(id);
			}
		}
		
	});
	
	// Now fetch all of the data
	this.pullDataAndUpdate();
};

TiePointMain.prototype.setActiveControlPoint = function(ctrlPt) {
	for (var i = 0; i < this.numImagesToDisplay; i++) {
		var imgEditor = this.imageEditors[i];
		imgEditor.setActiveControlPoint(ctrlPt);
	}
	
	this.mapViewer.setActiveControlPoint(ctrlPt);
}

TiePointMain.prototype.globalSelectControlPoint = function(ctrlPt) {
	this.controlPointOptions.selectPoint(ctrlPt.id);
};

TiePointMain.prototype.completeTiePointEdit = function() {
	if (this.activeImageEditor) {
		console.log("Completed tie point edit.");
		this.activeImageEditor.commitTiePointEdits(this.editedControlPoint);
	} else {
		console.log("Stray event for terminating tie point edit.  Ignoring.");
	}
}

TiePointMain.prototype.startTiePointEdit = function(activeEditor, controlPoint) {
	this.activeImageEditor = activeEditor;
	this.editedControlPoint = controlPoint;
}

TiePointMain.prototype.updateTiePoint = function(img, tiePoint) {
	this.mapViewer.handleTiePointUpdate(img, tiePoint);
}

TiePointMain.prototype.toggleTiePoint = function(img, tiePoint, show) {
	this.mapViewer.toggleTiePoint(img, tiePoint, show);
}

function displayImage(imgNdx) {
	mainViewer.displayImage(imgNdx);
}

function handleControlPointSelection(ctrlPt) {
	if (ctrlPt == null) {
		$('#controlPointEditingStatus').html("No Control Point is active.");
	} else {
		$('#controlPointEditingStatus').html("Control point " + ctrlPt.name + " is active.");
	}
	mainViewer.setActiveControlPoint(ctrlPt);
};

function handleImageFiltering(filterImagesToActive) {
	//console.log("Filtering to active control point = " + filterImagesToActive);
	//alert("Not implemented yet");
	// TODO - notify map and image viewer
}

function refreshDisplay() {
	mainViewer.showHideMapDisplay();
}


