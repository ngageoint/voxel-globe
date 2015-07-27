// Override the OpenLayers 3 selection handling to ensure that we always have 1 element selected when we click...
/**
 * @inheritDoc
 */
ol.interaction.Select.prototype.handleMapBrowserEvent = function(
		mapBrowserEvent) {
	if (!this.condition_(mapBrowserEvent)) {
		return true;
	}
	var add = this.addCondition_(mapBrowserEvent);
	var remove = this.removeCondition_(mapBrowserEvent);
	var toggle = this.toggleCondition_(mapBrowserEvent);
	var set = !add && !remove && !toggle;
	var map = mapBrowserEvent.map;
	var features = this.featureOverlay_.getFeatures();
	if (set) {
		// Replace the currently selected feature(s) with the feature at the
		// pixel,
		// or clear the selected feature(s) if there is no feature at the pixel.
		/** @type {ol.Feature|undefined} */
		var feature = map.forEachFeatureAtPixel(mapBrowserEvent.pixel,
		/**
		 * @param {ol.Feature}
		 *            feature Feature.
		 * @param {ol.layer.Layer}
		 *            layer Layer.
		 */
		function(feature, layer) {
			return feature;
		}, undefined, this.layerFilter_);
		if (goog.isDef(feature) && features.getLength() == 1
				&& features.item(0) == feature) {
			// No change
		} else {
			// if (features.getLength() !== 0) {
			// features.clear();
			// }
			if (goog.isDef(feature)) {
				if (features.getLength() !== 0) {
					features.clear();
				}
				// If we click on a feature, globally select that control point
				if (feature.controlPoint) {
					mainViewer.globalSelectControlPoint(feature.controlPoint);
				}
			}
		}
	} else {
		// Modify the currently selected feature(s).
		map.forEachFeatureAtPixel(mapBrowserEvent.pixel,
		/**
		 * @param {ol.Feature}
		 *            feature Feature.
		 * @param {ol.layer.Layer}
		 *            layer Layer.
		 */
		function(feature, layer) {
			var index = goog.array.indexOf(features.getArray(), feature);
			if (index == -1) {
				if (add || toggle) {
					features.push(feature);
				}
			} else {
				if (remove || toggle) {
					features.removeAt(index);
				}
			}
		}, undefined, this.layerFilter_);
	}
	return false;
};

/**
 * Override the OpenLayers 3 modification to notify when the modification is
 * complete so we can commit the changes.
 */
/**
 * @inheritDoc
 */
ol.interaction.Modify.prototype.handlePointerUp = function(evt) {
	var segmentData;
	for (var i = this.dragSegments_.length - 1; i >= 0; --i) {
		segmentData = this.dragSegments_[i][0];
		this.rBush_.update(ol.extent.boundingExtent(segmentData.segment),
				segmentData);
	}
	mainViewer.completeTiePointEdit();
	return false;
};

function TiePointEditor(imageContainerDivName, editorCount) {
	this.divName = "imageWrapper" + editorCount;
	this.toolbarDivName = "imageToolbar" + editorCount;
	this.imageDivName = "image" + editorCount;
	this.addButton = "addPoint" + editorCount;
	this.removeButton = "removePoint" + editorCount;
	this.saveButton = "savePoint" + editorCount;
	this.cancelButton = "cancelPoint" + editorCount;
	this.imageNameField = "imageName" + editorCount;
	this.editorId = editorCount;
	this.activeControlPoint = null;
	this.img = null;
	this.isInitializing = false;

	var divText = '<div id="' + this.divName
			+ '" class="imageWidget"><div id="' + this.imageDivName
			+ '" class="imageContents"></div><div id="' + this.toolbarDivName
			+ '" class="imageToolbar"></div></div>';
	$('#' + imageContainerDivName).append(divText);
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

	var imgsource = new ol.source.Zoomify({
		url : url,
		size : [ imgWidth, imgHeight ],
		crossOriginKeyword : crossOrigin
	});

	var imgtile = new ol.layer.Tile({
		source : imgsource
	});

	this.drawsource = new ol.source.Vector();
	var inactiveStyle = new ol.style.Style({
//		image: new ol.style.Icon({
//		    anchor: [0.5, 0.5],
//		    anchorXUnits: 'fraction',
//		    anchorYUnits: 'fraction',
//		    opacity: 0.75,
//		    src: iconFolderUrl + "inactiveCtrlPt.png"
//		  })
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
//		image: new ol.style.Icon({
//		    anchor: [0.5, 0.5],
//		    anchorXUnits: 'fraction',
//		    anchorYUnits: 'fraction',
//		    opacity: 0.75,
//		    src: iconFolderUrl + "activeCtrlPt.png"
//		  })
	});
	
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

	this.select = new ol.interaction.Select({
		toggleCondition : ol.events.condition.never,
		style : activeStyle
	});
	// get the features from the select interaction
	var selected_features = this.select.getFeatures();

	// when a feature is selected...
	selected_features.on('add', function(e) {
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
	});

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
	$('#' + this.toolbarDivName)
			.append(
					'<br><label class="imageToolbarLabel">' + this.imgName
							+ '</label>');
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
	// feature.controlPoint = controlPoints[tiePoint.fields.geoPoint];
	// data.feature = feature;
	// console.log("Attempted to create a feature");
	// }
	// }
	// }
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
				editorState[tiePoint.fields.geoPoint] = {
					tiePoint : tiePoint
				};
				var point = tiePoint.fields.point.coordinates;
				var feature = new ol.Feature({
					geometry : new ol.geom.Point([ point[0], -1 * point[1] ]),
					geoPoint : tiePoint.fields.geoPoint
				});
				feature.controlPoint = controlPoints[tiePoint.fields.geoPoint];
				editorState[tiePoint.fields.geoPoint].feature = feature;
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
	/*if (this.drawsource) {
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
	}*/
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
				this.select.getFeatures().push(
						this.editorState[cp.id].feature);
				$('#' + this.addButton).prop("disabled", "disabled");
				$('#' + this.removeButton).prop("disabled", "");
			} else {
				$('#' + this.addButton).prop("disabled", "");
				$('#' + this.removeButton).prop("disabled", "disabled");
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
	var farray = this.drawsource.getFeatures();
	var point = null;
	for (var i = 0; i < farray.length; i++) {
		point = farray[i].getGeometry().getCoordinates();
	}
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
										if (data[i].fields.geoPoint == feature.controlPoint.id) {
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
										if (data[i].fields.geoPoint == feature.controlPoint.id) {
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
