/*
 * The Tie point editor is the main class for an individual OL3 imageviewer
 */

function TiePointEditor(imageContainerDivName, editorCount) {
	this.divName = "imageWrapper" + editorCount;
	this.toolbarDivName = "imageToolbar" + editorCount;
	this.imageDivName = "image" + editorCount;
	this.addButton = "addPoint" + editorCount;
	this.removeButton = "removePoint" + editorCount;
	this.saveButton = "savePoint" + editorCount;
	this.cancelButton = "cancelPoint" + editorCount;
	this.imageNameField = "imageName" + editorCount;
	this.bannerDivName = "imgBanner" + editorCount;
	this.editorId = editorCount;
	this.activeControlPoint = null;
	this.img = null;
	this.isInitializing = false;

	var divText = '<div id="' + this.divName
			+ '" class="imageWidget"><div id="' + this.imageDivName
			+ '" class="imageContents"></div><div id="' + this.toolbarDivName
			+ '" class="imageToolbar"></div></div>';
	$('#' + imageContainerDivName).append(divText);

	$('#' + this.divName).append('<div id="' + this.bannerDivName + '" class="imgBanner">' + 
		'<img src="' + iconFolderUrl + 'planet.svg">' + 
		'<div class="p1">Includes material ©2016 Planet Labs Inc. All rights reserved.</div>' +
		'<div class="p2">DISTRIBUTION STATEMENT C: Distribution authorized to U.S. Government Agencies and their contractors (Administrative or Operational Use) Other requests for this document shall be referred to AFRL, Wright-Patterson Air Force Base, OH 45433-7321.</div></div>')
}

TiePointEditor.prototype.initialize = function(img, controlPoints) {
	if (this.isInitialzing) {
		return;
	}
	this.isInitializing = true;
	console.log("Initializing image " + img.name);
	$('#' + this.imageDivName).html("");
	$('#' + this.toolbarDivName).html("");
	$('#' + this.toolbarDivName).toggle(true);
	$('#' + this.bannerDivName).show();

	this.imgWidth = img.width;
	this.imgHeight = img.height;
	this.imgUrl = img.url;
	this.img = img;

	this.editorState = {};

	var imgWidth = this.imgWidth;
	var imgHeight = this.imgHeight;
	this.imgName = img.name;
	var url = this.imgUrl;
	var crossOrigin = 'anonymous';
	var that = this;
	this.selectedFeature = null;

	var imgCenter = [ imgWidth / 2, -imgHeight / 2 ];

	// Maps always need a projection, but Zoomify layers are not geo-referenced,
	// and
	// are only measured in pixels. So, we create a fake projection that the map
	// can use to properly display the layer.
	var proj = new ol.proj.Projection({
		code : 'ZOOMIFY',
		units : 'pixels',
		extent : [ 0, 0, imgWidth, imgHeight ]
	});

	//Zoomify image source
	var imgsource = new ol.source.Zoomify({
		url : url,
		size : [ imgWidth, imgHeight ],
		crossOriginKeyword : crossOrigin
	});

	//Creates the actual layer to get rendered, for tiled images
	var imgtile = new ol.layer.Tile({
		source : imgsource
	});

	//a vector of features, start with no features
	this.drawsource = new ol.source.Vector();

  //Styles for tie points
	var inactiveStyle = new ol.style.Style({
		image : new ol.style.Circle({
			radius : 7,
			stroke : new ol.style.Stroke({
				color : INACTIVE_COLOR,
				width : 3
			})
		})
	});
	var activeStyle = new ol.style.Style({
		image : new ol.style.Circle({
			radius : 7,
			stroke : new ol.style.Stroke({
				color : ACTIVE_COLOR,
				width : 3
			})
		})
	});
	
	//Creates the actual layer to get rendered, for tiled images
	var vector = new ol.layer.Vector({
		source : that.drawsource,
		style : inactiveStyle
	});

	// populate drawsource with tie point information
	// for (var pt in this.editorState) {
	// var data = this.editorState[pt];
	// if (data.feature) {
	// that.drawsource.addFeature(data.feature);
	// }
	// }


  //This seems to handle events on the entire map, not just a feature?
	this.select = new ol.interaction.Select({
		condition : ol.events.condition.singleClick,
		addCondition : ol.events.condition.singleClick,
		removeCondition : ol.events.condition.never,
		toggleCondition : ol.events.condition.never,
		style : activeStyle
	});

  //This is triggered when an inactive point is clicked.
  //This is one way the active control point is changed.
	this.select.on('select', function (e) {
		// get the feature
		var feature = e.selected[0];
		if (feature != null) {
			$('#controlPointEditingStatus').html(
					"Selected a tie point " + feature.controlPoint.name
							+ " in image " + that.imgName);
			that.selectedFeature = feature;
			if (feature.controlPoint) {
					mainViewer.globalSelectControlPoint(feature.controlPoint);

			// ...listen for changes on it
				mainViewer.startTiePointEdit(that, feature.controlPoint);
				$('#controlPointEditingStatus').html(
						"Editing a tie point in image " + feature.controlPoint.name
								+ " in " + that.imgName);
//		});
			}
		}
	}); 

  //I resurrected this, not that I understand any of it.
  //It's important because it makes sure that.selectedFeature is set correctly
  //When a new feature is added. I'm think some functionality is repeated 
  //In the previous this.select.on event, but maybe it's needed in both?
	this.select.getFeatures().on('add', function(e) {
		console.log('AEN: Feature Added');
		// get the feature
		var feature = e.element;
		$('#controlPointEditingStatus').html(
				"Selected a tie point " + feature.controlPoint.name
						+ " in image " + that.imgName);
		that.selectedFeature = feature;
		// ...listen for changes on it
		feature.on('change', function(e) {
			mainViewer.startTiePointEdit(that, feature.controlPoint);
			$('#controlPointEditingStatus').html(
					"Editing a tie point in image " + feature.controlPoint.name
							+ " in " + that.imgName);
	  });
	});

	this.modify = new ol.interaction.Modify({
		features : that.select.getFeatures(),
		style : activeStyle
	});

	this.modify.on('modifyend', function(e) {	
		mainViewer.completeTiePointEdit();
	});

	this.map = new ol.Map({
		interactions : ol.interaction.defaults().extend(
				[ that.select, that.modify ]),
		layers : [ imgtile, vector ],
		target : this.imageDivName,
		controls : [], // Disable default controls
		view : new ol.View({
			projection : proj,
			center : imgCenter,
			zoom : 1
		})
	});
	//I have NO clue what I'm doing here https://groups.google.com/forum/#!topic/ol3-dev/SEu5Js8OurU
  this.map.renderSync();
  //If I don't do this, coordinate will turn up null deep in ol because the mapping of
  //pixels to coordinates is not yet initialized. This then breaks a lot of code
  //By renderSync here, the pixel conversion code works and everything is happy.

  //This is used when adding a new point
	var pointDrawingTool = new ol.interaction.Draw({
		source : that.drawsource,
		type : "Point" // can also be LineString, Polygon someday
	}); // global so we can remove it later


	pointDrawingTool.on('drawend', function(e) {
		// make the drawn feature a candidate for
		// modification
		that.currentAction = null;
		that.selectedFeature = e.feature;
		e.feature.controlPoint = that.activeControlPoint;
		that.editorState[that.activeControlPoint.id] = {
			feature : e.feature
		};
		that.map.removeInteraction(pointDrawingTool);
		that.select.getFeatures().clear();
		that.map.addInteraction(that.select);
		that.select.getFeatures().push(e.feature); // Make sure it continues to
													// be selected
		$('#' + that.addButton).prop("disabled", "disabled");
		$('#' + that.removeButton).prop("disabled", "");
		that.createTiePointFromFeature(e.feature);
		mainViewer.startTiePointEdit(that, e.feature.controlPoint);
//		});
	});

	if (controlPoints) {
		// Set up the image editor toolbar buttons
		$('#' + this.toolbarDivName).append(
				'<button id="' + this.addButton + '"><img height=12 src="' + iconFolderUrl + "plus.png" +'" style="vertical-align:middle;"></img></button>');
		$('#' + this.addButton)
				.click(
						function(e) {
							console.log("start drawing");
							that.currentAction = "add";
							if (that.activeControlPoint != null) {
								$('#controlPointEditingStatus').html(
										"Adding a correspondence for "
												+ that.activeControlPoint.name
												+ " to image " + that.imgName);
								that.map.removeInteraction(that.select);
								that.map.addInteraction(pointDrawingTool);
							} else {
								alert("An control point must be chosen before adding tie points.");
							}
						})
		$('#' + this.toolbarDivName).append(
				'<button id="' + this.removeButton + '"><img height=12 src="' + iconFolderUrl + "minus.png" +'" style="vertical-align:middle;"></img></button>');
		$('#' + this.removeButton).click(
				function(e) {
					console.log("remove selected point");

					if (that.selectedFeature != null) {
						that.removeTiePoint(that.selectedFeature.controlPoint);
						$('#controlPointEditingStatus').html(
								"Removed the correspondence for "
										+ that.activeControlPoint.name
										+ " to image " + that.imgName);
					}
				})
	}
	/*
	 * $('#' + this.toolbarDivName).append( '<span style="width:40px;"></span><button
	 * id="' + this.saveButton + '">Save</button>'); $('#' +
	 * this.saveButton).click(function(e) { console.log("save changes to the
	 * image"); $('#controlPointEditingStatus').html("Saved a correspondence for " +
	 * that.activeControlPoint.name + " to image " + that.imgName); }) $('#' +
	 * this.toolbarDivName).append( '<button id="' + this.cancelButton +
	 * '">Cancel</button>'); $('#' + this.cancelButton).click(function(e) {
	 * console.log("cancel changes to the image");
	 * $('#controlPointEditingStatus').html("Cancelled changes to the correspondence
	 * for " + that.activeControlPoint.name + " to image " + that.imgName); })
	 */

	if (mainViewer) {
		$('#' + this.toolbarDivName)
		.append(
				'<br><label class="imageToolbarLabel">' + this.imgName
						+ '</label>');
	}

	//	
	// if (img.editorState == null) {
	// img.editorState = {};
	// } else {
	// for (var pt in img.editorState) {
	// var data = img.editorState[pt];
	// if (data.tiePoint) {
	// // Create feature
	// var tiePoint = data.tiePoint;
	//				
	// feature.controlPoint = controlPoints[tiePoint.fields.control_point];
	// data.feature = feature;
	// console.log("Attempted to create a feature");
	// }
	// }
	// }
	if (mainViewer) {
		console.log("Fetching tie points for image " + img.id);
		$.ajax({
			type : "GET",
			url : "/meta/fetchTiePoints",
			data : {
				imageId : img.id
			},
			success : function(data) {
				console.log("Retrieved " + data.length + " tie points for image "
						+ img.id);
				var editorState = {};
				that.filteredFeatures = [];
				for (var k = 0; k < data.length; k++) {
					var tiePoint = data[k];
					editorState[tiePoint.fields.control_point] = {
						tiePoint : tiePoint
					};
					var point = tiePoint.fields.point.coordinates;
					var feature = new ol.Feature({
						geometry : new ol.geom.Point([ point[0], -1 * point[1] ]),
						control_point : tiePoint.fields.control_point
					});
					feature.controlPoint = controlPoints[tiePoint.fields.control_point];
					editorState[tiePoint.fields.control_point].feature = feature;
					if (feature.controlPoint.isInActiveSet) {
						that.drawsource.addFeature(feature);
						mainViewer.updateTiePoint(that.img, tiePoint);
					} else {
						that.filteredFeatures.push(feature);
					}
				}
				that.editorState = editorState;
				if (that.activeControlPoint != null) {
					that.setActiveControlPoint(that.activeControlPoint);
				}
				that.isInitializing = false;
				mainViewer.incrementImageInitialized();
			},
			dataType : 'json'
		});
	}
}

TiePointEditor.prototype.updateAvailableControlPoint = function(ctrlPt) {
	if (this.editorState != null) {
		var data = this.editorState[ctrlPt.id];
		if (data) {
			if (ctrlPt.isInActiveSet) {
				this.drawsource.addFeature(data.feature);
				mainViewer.toggleTiePoint(this.img, data.tiePoint, true);
			} else {
				this.drawsource.removeFeature(data.feature);
				mainViewer.toggleTiePoint(this.img, data.tiePoint, false);
			}
		} else {
			console.log("No data for control point " + ctrlPt.name);
		}
	}
}

TiePointEditor.prototype.markImageControlPointIds = function(keys) {
	for (var id in this.editorState) { // should be indexed by control point ID even if the point isn't visible
		keys[id] = true;
	}
}

TiePointEditor.prototype.blank = function() {
	this.activeControlPoint = null;
	this.img = null;
	this.isInitializing = false;
	this.editorState = {};
	$('#' + this.imageDivName).html("");
	$('#' + this.toolbarDivName).toggle(false);
	// $('#' + this.divName).toggle(false);
}

TiePointEditor.prototype.show = function(width, height) {
	$('#' + this.divName).css("height", height + '%');
	$('#' + this.divName).css("width", width + '%');
	$('#' + this.divName).toggle(true);
}

TiePointEditor.prototype.hide = function() {
	$('#' + this.divName).toggle(false);
}

TiePointEditor.prototype.getDebugInfo = function() {
	if (this.drawsource) {
		var farray = this.drawsource.getFeatures();
		var text = this.divName + '<br>';
		for (var i = 0; i < farray.length; i++) {
			var point = farray[i].getGeometry().getCoordinates();
			text += farray[i].controlPoint.name + " - " + point[0] + ", "
					+ point[1] + '<br>';
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

/**
 * Set the active control point
 */
TiePointEditor.prototype.setActiveControlPoint = function(cp) {
	this.activeControlPoint = cp;
	if (cp != null) {
		console.log("Set active control point for image editor");
		if (this.currentAction == "add") {
			$('#controlPointEditingStatus').html(
					"Adding a correspondence for "
							+ this.activeControlPoint.name + " to image "
							+ this.imgName)
		}
		if (this.drawsource && cp) {
			var farray = this.drawsource.getFeatures();
			this.select.getFeatures().clear();
			if (this.editorState[cp.id] && this.editorState[cp.id].feature) {
				this.select.getFeatures().push(this.editorState[cp.id].feature);
				$('#' + this.addButton).prop("disabled", "disabled");
				$('#' + this.removeButton).prop("disabled", "");
			} else {
				$('#' + this.addButton).prop("disabled", "");
				$('#' + this.removeButton).prop("disabled", "disabled");
			}
			if (cp.id in this.editorState) {
//				this.selectedFeature = this.editorState[cp.id].feature
				mainViewer.startTiePointEdit(this, this.editorState[cp.id].feature.controlPoint);
			}
		}
	} else {
		if (this.select) {
			this.select.getFeatures().clear();
			$('#' + this.addButton).prop("disabled", "disabled");
			$('#' + this.removeButton).prop("disabled", "disabled");
		}
	}
}

/**
 * Remove a tie point corresponding to a given control point.
 */
TiePointEditor.prototype.removeTiePoint = function(cp) {
	var that = this;
	var data = this.editorState[cp.id];
	var feature = data.feature;
	var tiePoint = data.tiePoint;
	if (this.drawsource && feature) {
		$.ajax({
			type : "GET",
			url : "/meta/deleteTiePoint",
			data : {
				id : tiePoint.pk
			},
			success : function(data) {
				console.log("Tie Point Removed");
				delete that.editorState[cp.id];
				that.select.getFeatures().clear();
				that.drawsource.removeFeature(feature);
				that.selectedFeature = null;
				$('#' + that.addButton).prop("disabled", "");
				$('#' + that.removeButton).prop("disabled", "disabled");
			},
			error : function() {
				alert("Unable to remove tie point");
			},
			dataType : 'html'
		});
	}
}

TiePointEditor.prototype.createTiePointFromFeature = function(feature) {
	var that = this;
//	var farray = this.drawsource.getFeatures();
	var point = null;
//	for (var i = 0; i < farray.length; i++) {
//		point = farray[i].getGeometry().getCoordinates();
//	}

	point = feature.getGeometry().getCoordinates();
	if (point != null) {
		console.log(this.img.id + ", " + feature.controlPoint.id + ", "
				+ Math.round(point[0]) + ", " + Math.round(-1 * point[1]));
		$.ajax({
					type : "GET",
					url : "/meta/createTiePoint",
					data : {
						imageId : that.img.id,
						controlPointId : feature.controlPoint.id,
						x : Math.round(point[0]),
						y : Math.round(-1 * point[1]),
						name : feature.controlPoint.name
					},
					success : function(data) {
						console.log("Tie Point Created");
						// Now fetch the result ???
						$.ajax({
									type : "GET",
									url : "/meta/fetchTiePoints",
									data : {
										imageId : that.img.id
									},
									success : function(data) {
										console.log("Retrieved tie points for image " + that.img.id);
										for (var i = 0; i < data.length; i++) {
											if (data[i].fields.control_point == feature.controlPoint.id) {
												that.editorState[feature.controlPoint.id].tiePoint = data[i];
												mainViewer.updateTiePoint(that.img, data[i]);
												break;
											}
										}
									},
									dataType : 'json'
								});
					},
					dataType : 'html'
				});
	} else {
		console.log("No features drawn");
	}
}

TiePointEditor.prototype.commitTiePointEdits = function(cp) {
	var that = this;
	var data = this.editorState[cp.id];
	var feature = data.feature;
	var point = data.feature.getGeometry().getCoordinates();
	console.log("Updating " + this.img.id + ", " + feature.controlPoint.id
			+ ", " + Math.round(point[0]) + ", " + Math.round(-1 * point[1]));
	$
			.ajax({
				type : "GET",
				url : "/meta/updateTiePoint",
				data : {
					tiePointId : data.tiePoint.pk,
					x : Math.round(point[0]),
					y : Math.round(-1 * point[1])
				},
				success : function(data) {
					console.log("Tie Point Updated");
					// Now fetch the result ???
					$
							.ajax({
								type : "GET",
								url : "/meta/fetchTiePoints",
								data : {
									imageId : that.img.id
								},
								success : function(data) {
									console
											.log("Retrieved tie points for image "
													+ that.img.id);
									for (var i = 0; i < data.length; i++) {
										if (data[i].fields.control_point == feature.controlPoint.id) {
											that.editorState[feature.controlPoint.id].tiePoint = data[i];
											mainViewer.updateTiePoint(that.img, data[i]);
											break;
										}
									}
								},
								dataType : 'json'
							});
				},
				dataType : 'html'
			});
}
