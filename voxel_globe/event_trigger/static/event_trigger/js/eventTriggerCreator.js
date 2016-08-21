var timeout;
var NUM_EDITORS = 4;
var REFERENCE_TYPE = "REFERENCE";
var EVENT_TYPE = "EVENT";
var ERROR_TYPE = "ERROR";

/**
 * This class supports the overall UI layout and data.
 */
function EventTriggerCreator() {
	this.imageEditors = [];
	this.sites = [];
	this.images = [];
	this.imagePaginator;
	this.numImagesToDisplay = 1;
	this.attributionModeChanged = false;
	this.displayingImage = 0;
	this.selectedImageSet = -1;
	this.selectedCameraSet = -1;
	this.imageWidths = [ 99, 49, 32, 24 ];
	this.imageHeights = [ 100, 100, 100, 100 ];
	this.bannerScale = [ 100, 90, 80, 70];
	this.configurationAction = null;
	
	this.activeImageEditor = null;
	this.displayCounter = 0;
	this.visibleImageCounter = 0;
	this.initializedImageCounter = 0;

	this.selectedTriggerSet = null;
	this.geometryFormInputs = null;
}

EventTriggerCreator.prototype.updateLayout = function() {
	this.numImagesToDisplay = parseInt($.trim($('#numImagesPerPage').val()));
  if (this.numImagesToDisplay > 1) {
    if (attributionMode != "small") {
      this.attributionModeChanged = true
    }
    attributionMode = "small";
  } else {
    if (attributionMode != "large") {
      this.attributionModeChanged = true
    }
    attributionMode = "large";
  }

	// console.log("Number of images to display " + this.numImagesToDisplay);
	for (var i = this.numImagesToDisplay; i < this.imageEditors.length; i++) {
		this.imageEditors[i].hide();
	}
	var width = this.imageWidths[this.numImagesToDisplay - 1];
	var height = this.imageHeights[this.numImagesToDisplay - 1];
	var scale = this.bannerScale[this.numImagesToDisplay - 1];

	for (var i = 0; i < this.numImagesToDisplay; i++) {
		this.imageEditors[i].show(width, height, scale);
	}
	this.displayImage(0);
	//this.imagePaginator.initialize(this.images.length, this.numImagesToDisplay, this.displayingImage, displayImage);
}

EventTriggerCreator.prototype.displayImage = function(imgNdx) {
	console.log("Displaying image " + imgNdx);
	this.displayCounter++;

	var that = this;
	var j = imgNdx;
	this.initializedImageCounter = 0;
	for (var i = 0; i < this.numImagesToDisplay; i++) {
		var imgEditor = this.imageEditors[i];
		var img = this.images[j];
		if (img) {
			if (!imgEditor.img || img.name != imgEditor.img.name || 
					imgEditor.editorState.selectedSite != this.selectedSite ||
					this.attributionModeChanged) {
				console.log('initializing');
				img.displayCounter = this.displayCounter;
				imgEditor.initialize(this.selectedImageSet, img, this.selectedSite, this.selectedCameraSet);	
      } else {
      	if (imgEditor.map) {
          imgEditor.map.updateSize();
        }
      }
		} else {
			console.log('no img');
			imgEditor.blank();
		}
		j++;
	}
};

EventTriggerCreator.prototype.handleAddGeometry = function(geometry) {
	for (var i = 0; i < this.numImagesToDisplay; i++) {
		var imgEditor = this.imageEditors[i];
		this.loadGeometryForImage(geometry, imgEditor.editorState.imageId, function(geo) {
			imgEditor.addGeometry(geometry);
		});
	}	
}

EventTriggerCreator.prototype.handleRemoveGeometry = function(geometry) {
	for (var i = 0; i < this.numImagesToDisplay; i++) {
		var imgEditor = this.imageEditors[i];
		this.loadGeometryForImage(geometry, imgEditor.editorState.imageId, function(geo) {
			imgEditor.removeGeometry(geometry);
		});
	}	
}

EventTriggerCreator.prototype.handleUpdateGeometry = function(geometry) {
	for (var i = 0; i < this.numImagesToDisplay; i++) {
		var imgEditor = this.imageEditors[i];
		this.loadGeometryForImage(geometry, imgEditor.editorState.imageId, function(geo) {
			imgEditor.updateGeometry(geometry);
		});
	}	
}

EventTriggerCreator.prototype.incrementImageInitialized = function() {
	this.initializedImageCounter++;	
	if (this.initializedImageCounter == this.visibleImageCounter) {
		this.updateWhenAllImagesInitialized();
	}
}

/**
 * Called when all image viewers have finished pulling their data and initializing completely.
 */
EventTriggerCreator.prototype.updateWhenAllImagesInitialized = function() {	
	refreshDisplay();
}


EventTriggerCreator.prototype.pullDataAndUpdate = function() {
	var that = this;
	$.ajax({
		type : "GET",
		url : "/meta/rest/auto/sattelsite/",
		data : {},
		success : function(data) {
			that.sites = data;
			if (that.sites.length > 0) {
				that.initializeSiteSelector();
			} else {
				$('#videoList').html("No sites found in the database.");
			}
		},
		dataType : 'json'
	});
};

EventTriggerCreator.prototype.initializeDataAndEvents = function() {

	for (var i = 0; i < NUM_EDITORS; i++) {
		var imgEditor = new EventTriggerEditor(this, "imageContainer", i);
		this.imageEditors.push(imgEditor);
	}
	//this.imagePaginator = new Paginator({div : "paginator", id : "1"});
	
	// wire in dynamic layout and page
	this.updateLayout();

	// Set up the initial state
	var that = this;
	$('#editorContentDiv').css("height", $(window).height() - 160 + "px");
	$('#editorContentDiv').css("width", $(window).width() - 30 + "px");
	$(window).resize(function(e) {
		$('#editorContentDiv').css("height", $(window).height() - 160 + "px");
		$('#editorContentDiv').css("width",  $(window).width() - 30 + "px");
		clearTimeout(timeout);
		timeout = setTimeout(refreshDisplay, 300);
	});

	//this.imagePaginator.initialize(0, this.numImagesToDisplay, this.displayingImage, new function() {});

	$('#loadOptions').toggle(true);
	$('#sideControlsContentDiv').toggle(true);
	this.activeSelector = "video";

	$('#videoList').html("Downloading video list...");

	// Set up all of the events...
	$('#numImagesPerPage').change(function(e) {		
		var num = parseInt($.trim($('#numImagesPerPage').val()));
		if (num >= 1 && num <= 4) {
			that.updateLayout();
		} else {
			alert("The number of displayed images should be between 1 and 4");
		}
	});

	$('#videoSelectorDiv').mousedown(function(e) {
		console.log("Selecting video selector...");
		if (that.activeSelector == "video") {
			that.handleConfigureComplete();
		} else {
			$('#loadOptions').toggle(true);
			if (that.activeSelector == null) {
				$('#sideControlsContentDiv').show("slide", {}, 300);
			}
			that.activeSelector = "video";
		}
	});

	$('#hideSelector').click(function (e) {
		that.handleConfigureComplete();
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

	var that = this;
	
	this.geometryDialog = $( "#triggerFormDiv" ).dialog({
	  autoOpen: false,
      width: 550,
      modal: true,
      buttons: {
        "OK": saveTriggerFormProperties,
        Cancel: function() {
          that.geometryDialog.dialog( "close" );
          that.geometryFormInputs = null;
        }
      },
      close: function() {
        that.form[ 0 ].reset();
      }
  	});

  	this.form = this.geometryDialog.find( "form" ).on( "submit", function( event ) {
      event.preventDefault();
      saveTriggerFormProperties();
    });

    $('#trigger_height').change(function() {
		var val = $('#trigger_height').val();
		if (!$.isNumeric(val) || val < 0 || val > 9999) {
			alert("Height must be between 0 and 9999 meters.");
			//$('#trigger_height').val(that.editorState.shapeHeight);
		} 
	});

	this.triggerSetDialog = $( "#triggerSetFormDiv" ).dialog({
	  autoOpen: false,
      width: 550,
      modal: true,
      buttons: {
        "OK": createTriggerSet,
        Cancel: function() {
          that.triggerSetDialog.dialog( "close" );
        }
      },
      close: function() {
        that.triggerSetForm[ 0 ].reset();
      }
  	});

  	this.triggerSetForm = this.geometryDialog.find( "form" ).on( "submit", function( event ) {
      event.preventDefault();
      createTriggerSet();
    });
	
	$('#editTriggerProperties').click(function (e) {
		if (that.selectedGeometry != null) {
			that.editEventTriggerProperties();
		}
	});

	$('#createTriggerSetButton').click(function (e) {
		that.triggerSetDialog.dialog( "open" );
	});

	// Now fetch all of the data
	this.pullDataAndUpdate();
};

EventTriggerCreator.prototype.handleConfigureComplete = function() {
	if (this.selectedSite != null && this.selectedTriggerSet != null) {
		$('#sideControlsContentDiv').hide("slide", {}, 300);
		$('#loadOptions').toggle(false);
		this.activeSelector = null;
	} else {
		alert("A Site and Trigger Set must be selected before proceeding.");
	}
};

EventTriggerCreator.prototype.initializeSiteSelector = function() {
	$('#videoList').html('Sites<br><select id="id_site_set" '+
			'onchange="mainViewer.chooseVideoToDisplay()"><option value="">--------</option></select><br>'); //+
   //    'Camera Set<br><select disabled id="id_camera_set"'+
			// 'onchange="mainViewer.chooseVideoToDisplay($('+"'"+'#id_image_set'+"'"+').val())"><option value="">--------</option></select>');
	for (var i = 0; i < this.sites.length; i++) {
		$('#id_site_set').append($("<option />").val(i).text(this.sites[i].name));
	}
};

EventTriggerCreator.prototype.initializeTriggerSelector = function() {
	$('#triggerList').html('Triggers<br><select id="id_trigger_set" '+
			'onchange="mainViewer.chooseTrigger()"><option value="">--------</option></select><br>'); //+
   //    'Camera Set<br><select disabled id="id_camera_set"'+
			// 'onchange="mainViewer.chooseVideoToDisplay($('+"'"+'#id_image_set'+"'"+').val())"><option value="">--------</option></select>');
	var selectedIndex = null;
	for (var i = 0; i < this.triggers.length; i++) {
		$('#id_trigger_set').append($("<option />").val(i).text(this.triggers[i].name));
		if (this.triggers[i].id == this.triggerId) {
			selectedIndex = i;
		}
	}

	if (selectedIndex != null) {
		$('#id_trigger_set').val(selectedIndex);
		this.chooseTrigger();
	}
};

EventTriggerCreator.prototype.chooseVideoToDisplay = function() {
	// this.numImagesToDisplay = 1;
	// $("#numImagesPerPage").val(1);
	siteIndex = $('#id_site_set').val();
	this.selectedSite = this.sites[siteIndex].id
	this.selectedImageSet = this.sites[siteIndex].image_set
	this.selectedCameraSet = this.sites[siteIndex].camera_set
	this.images = [];
	var that = this;
	$.ajax({
		type : "GET",
		url : "/meta/rest/auto/image",
		data : {
			imageset : this.selectedImageSet
		},
		success : function(data) {
			// Toggle all other image selection buttons
			if (data.error) {
				alert(data.error);
			} else {				
				that.images = data;
				if (that.images.length > 0) {
					//that.imagePaginator.initialize(that.images.length, that.numImagesToDisplay, 0, displayImage);
					that.displayImage(0);
					if (that.images.length < 4) {
						$("#numImagesPerPage").attr('max', that.images.length);
					} else {
						$("#numImagesPerPage").attr('max', 4);
					}
				} else {
					$('#imageWidget').html("No images found in the database.");
				}
			}
		},
		dataType : 'json'
	});

	this.populateTriggerSelector(null);
};

// TODO, need to add ability to draw all triggers once it is has been updated...

EventTriggerCreator.prototype.chooseTrigger = function() {
	triggerIndex = $('#id_trigger_set').val();
	if (triggerIndex != null) {
		this.triggerId = this.triggers[triggerIndex].id;
		console.log("Trigger " + this.triggerId + " chosen.");
		var that = this;
		this.updateSelectedTriggerObject(function() {
			that.loadAllTriggerGeometries();
		});
	}
}

EventTriggerCreator.prototype.populateTriggerSelector = function(initialTrigger) {
	this.triggerId = initialTrigger;
	var that = this;
	$.ajax({
		type : "GET",
		url : "/meta/rest/auto/satteleventtrigger/",
		data : {
			site : this.selectedSite
		},
		success : function(data) {
			$('#eventTriggerSelectorDiv').toggle(true);
			that.triggers = data;
			if (that.triggers.length > 0) {
				that.initializeTriggerSelector();
			} else {
				$('#triggerList').html("No triggers found in the database.");
			}
		},
		dataType : 'json'
	});
}

EventTriggerCreator.prototype.loadAllTriggerGeometries = function() {
	var that = this;
	for (var i = 0; i < that.selectedTriggerSet.reference_areas.length; i++) {
		that.loadGeometry(that.selectedTriggerSet.reference_areas[i], function(geometry) {
			that.handleAddGeometry(geometry);
		});
	}
	for (var i = 0; i < that.selectedTriggerSet.event_areas.length; i++) {
		that.loadGeometry(that.selectedTriggerSet.event_areas[i], function(geometry) {
			that.handleAddGeometry(geometry);
		});
	}
};

EventTriggerCreator.prototype.updateSelectedTriggerObject = function(callbackOnSuccess) {
	var that = this;
	$.ajax({
		type : "GET",
		url : "/meta/rest/auto/satteleventtrigger/",
		data : {
			id : this.triggerId
		},
		success : function(data) {
			that.selectedTriggerSet = data[0];
			if (callbackOnSuccess) {
				callbackOnSuccess();
			}
		},
		dataType : 'json'
	});
};

EventTriggerCreator.prototype.updateGeometryShape = function(geometry, newShape, commitToTrigger) {
	var that = this;

	if (geometry != null) {

		$.ajax({
			type : "POST",
			url : "/apps/event_trigger/update_geometry_polygon",
			data : {
				image_id : that.activeEditor.editorState.imageId,
				points : newShape,
				sattelgeometryobject_id : geometry.id,				
				site_id : that.selectedSite,
				projection_mode : "z-plane",
				height : geometry.height
			},
			success : function(data) {
				console.log("Geometry updated");

				that.loadGeometry(geometry.id, function(db_geo) {
					that.setSelectedGeometry(db_geo);
					if (commitToTrigger) {
						db_geo.type = geometry.type;
						that.addGeometryToTrigger(db_geo.type, db_geo);
						that.handleAddGeometry(db_geo);
					} else {
						that.handleUpdateGeometry(db_geo);
					}					
				});
			},
			error : function() {
				alert("Unable to modify geometry");
			},
			dataType : 'json'
		});
	} else {
		alert("Could not update geometry.");
	}
};

EventTriggerCreator.prototype.commitGeometryPropertyChanges = function() {
	if (that.geometryFormInputs != null && that.selectedGeometry != null) {

		var bogus_origin = "POINT(0 0 0)";

		var that = this;
		// Create the polygon, update it, and add it to the trigger
		$.ajax({
			type : "PATCH",
			url : "/meta/rest/auto/sattelgeometryobject/" + this.selectedGeometry.id + "/",
			data : {
				name : this.geometryFormInputs.name,
				description : this.geometryFormInputs.desc, 
				height : this.geometryFormInputs.height, 
				site : this.selectedSite,
				origin : bogus_origin
			},
			success : function(data) {
				alert("Geometry Updated id=" + data.id);

				if (this.selectedGeometry.height != this.geometryFormInputs.height) {
					// TODO Need to refresh geometry...
				}
				that.loadGeometry(data.id, this.geometryFormInputs.type, function(geometry) {
					that.setSelectedGeometry(geometry);
				});
			},
			error : function() {
				alert("Unable to create geometry");
			},
			dataType : 'json'
		});
	}
};

EventTriggerCreator.prototype.addGeometryToTrigger = function(type, geometry) {
	var that = this;
	var updates = {
	};
	if (that.selectedTriggerSet) {
		if (type == REFERENCE_TYPE) {
			that.selectedTriggerSet.reference_areas.push(geometry.id);
			updates.reference_areas = that.selectedTriggerSet.reference_areas;
			console.log("Updates to trigger: " + updates);
		} else if (type == EVENT_TYPE) {
			that.selectedTriggerSet.event_areas.push(geometry.id);
			updates.event_areas = that.selectedTriggerSet.event_areas;
			console.log("Updates to trigger: " + updates);
		} else {
			alert("Unknown geometry type " + type);
			return;
		}

//TODO: Undo when upgrading past DRF 3.3???
    var hack = {
   	};
   	hack._method = "PATCH";
   	hack._content_type = "application/json";
   	hack._content=JSON.stringify(updates);
		$.ajax({
			//type : "PATCH",
			type : "POST",
			url : "/meta/rest/auto/satteleventtrigger/" + that.selectedTriggerSet.id + "/",
			data : hack,
			success : function(data) {
				alert("Trigger updated");
				that.updateSelectedTriggerObject();
			},
			error : function() {
				alert("Unable to modify trigger");
			},
			dataType : 'json'
		});
	} else {
		alert("Could not add " + type + " area to trigger.");
	}
}

EventTriggerCreator.prototype.createEventTrigger = function(geometryString) {
	var bogus_origin = "POINT(0 0 0)";

	var that = this;
	// Create the polygon, update it, and add it to the trigger
	$.ajax({
		type : "POST",
		url : "/meta/rest/auto/sattelgeometryobject/",
		data : {
			name : this.geometryFormInputs.name,
			description : this.geometryFormInputs.desc, 
			site : this.selectedSite,
			height : this.geometryFormInputs.height,
			origin : bogus_origin
		},
		success : function(data) {
			alert("Geometry Created id=" + data.id);
			data.type = that.geometryFormInputs.type;
			that.updateGeometryShape(data, geometryString, true);
		},
		error : function() {
			alert("Unable to create geometry");
		},
		dataType : 'json'
	});
}

EventTriggerCreator.prototype.loadGeometryForImage = function(db_geo, imageId, callbackOnSuccess) {
	var that = this;
	$.ajax({
		type : "GET",
		url : "/apps/event_trigger/get_event_geometry",
		data : {
			image_id : imageId,
			sattelgeometryobject_id : db_geo.id,
			site_id : that.selectedSite
		},
		success : function(pts) {
			db_geo.imgCoords[imageId] = pts;
			if (callbackOnSuccess) {
				callbackOnSuccess(db_geo, imageId);
			}
			console.log("Loaded geometry " + db_geo.id + " " + imageId + " coords: " + db_geo.imgCoords[imageId]);
		},
		error : function() {
			alert("Unable to load geometry" + db_geo.id + " " + imageId);
		},
		dataType : 'json'
	});
}

EventTriggerCreator.prototype.loadGeometry = function(geometryId, callbackOnSuccess) {
	var that = this;
	$.ajax({
		type : "GET",
		url : "/meta/rest/auto/sattelgeometryobject/",
		data : {
			id : geometryId,
		},
		success : function(data) {
			var db_geo = data[0];

			if (that.selectedTriggerSet.reference_areas.indexOf(geometryId) >= 0) {
				db_geo.type = REFERENCE_TYPE;
			} else if (that.selectedTriggerSet.event_areas.indexOf(geometryId) >= 0) {
				db_geo.type = EVENT_TYPE;
			} else {
				db_geo.type = ERROR_TYPE;
			}
			db_geo.imgCoords = {};
			
			if (callbackOnSuccess) {
				callbackOnSuccess(db_geo);
			}
			console.log("Loaded geometry " + db_geo.id);
		},
		error : function() {
			alert("Unable to retrieve geometry");
		},
		dataType : 'json'
	});
}

EventTriggerCreator.prototype.setSelectedGeometry = function(db_geo) {
	this.selectedGeometry = db_geo;
	if (this.selectedGeometry) {
		$('#triggerDetails').html("Selected " + this.selectedGeometry.name + ": " + this.selectedGeometry.description);
	} else {
		$('#triggerDetails').html("");
	}
}

EventTriggerCreator.prototype.setActiveEditor = function(editor, geo) {
	this.activeEditor = editor;
	this.setSelectedGeometry(geo);
}

EventTriggerCreator.prototype.createEventTriggerProperties = function() {
	if (this.activeEditor) {
		this.isCreatingGeometry = true;
		this.geometryDialog.dialog( "open" );
	} else {
		alert("No editor has been activated.");
	}
}

EventTriggerCreator.prototype.editEventTriggerProperties = function() {	
	this.isCreatingGeometry = false;
	$('#trigger_name').val(this.selectedGeometry.name);
	$('#trigger_desc').val(this.selectedGeometry.description);
	$('#trigger_type').val(this.selectedGeometry.type);
	$('#trigger_height').val(this.selectedGeometry.height);
	
	$("#trigger_height").attr("disabled", "disabled");
	$("#trigger_type").attr("disabled", "disabled");
	this.geometryDialog.dialog( "open" );
}

EventTriggerCreator.prototype.handleGeometryFormComplete = function() {
	if (this.isCreatingGeometry) {
		// Finish drawing then commit changes
		this.activeEditor.drawGeometry();	
	} else {
		this.geometryDialog.dialog( "close" );
		this.commitGeometryPropertyChanges();
	}
}

// Global functions.

function refreshDisplay() {
	// for (var i = 0; i < mainViewer.imageEditors.length; i++) {
	// 	mainViewer.imageEditors[i].resize();
	// }
	mainViewer.displayImage(0);
}

function displayImage(imgNdx) {
	mainViewer.displayImage(imgNdx);
}

function saveTriggerFormProperties() {
	mainViewer.geometryFormInputs = {};
	mainViewer.geometryFormInputs.name = $('#trigger_name').val();
	mainViewer.geometryFormInputs.desc = $('#trigger_desc').val();
	mainViewer.geometryFormInputs.height = $('#trigger_height').val();
	var e = document.getElementById("trigger_type");
	mainViewer.geometryFormInputs.type = e.options[e.selectedIndex].value;
    mainViewer.geometryDialog.dialog( "close" );
    mainViewer.handleGeometryFormComplete();
}

function createTriggerSet() {
	var name = $('#trigger_set_name').val();
	var desc = $('#trigger_set_desc').val();
	var site_id = mainViewer.selectedSite;
	var bogus_origin = "POINT(0 0 0)";
	var bogus_ref_img = mainViewer.images[0].id;

    mainViewer.triggerSetDialog.dialog( "close" );
	
	$.ajaxSetup({
	    beforeSend: function(xhr, settings) {
	      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
	        xhr.setRequestHeader("X-CSRFToken", csrftoken);
	      }
	    }
  	});

	$.ajax({
			type : "POST",
			url : "/meta/rest/auto/satteleventtrigger/",
			data : {
				name : name,
				description : desc, 
				site : site_id,
				origin : bogus_origin,
				reference_image : bogus_ref_img
			},
			success : function(data) {
				alert("Event Trigger Created");
				mainViewer.populateTriggerSelector(data.id);
			},
			error : function() {
				alert("Unable to save event trigger");
			},
			dataType : 'json'
		});
}

// MARTHA Refactor into common js file

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie != '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) == (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

// End refactor request
