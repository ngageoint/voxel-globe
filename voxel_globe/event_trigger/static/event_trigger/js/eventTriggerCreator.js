var timeout;
var ACTIVE_COLOR = 'rgba(255, 255, 0, 0.9)';
var INACTIVE_COLOR = 'rgba(119, 204, 255, 0.75)';
var NUM_EDITORS = 4;
var REFERENCE_TYPE = "REFERENCE";

/**
 * This class supports the overall UI layout and data.
 */
function EventTriggerCreator() {
	this.imageEditors = [];
	this.sites = [];
	this.images = [];
	this.imagePaginator;
	this.numImagesToDisplay = 1;
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
	this.triggerGeometry = null;
}

EventTriggerCreator.prototype.updateLayout = function() {
	this.numImagesToDisplay = parseInt($.trim($('#numImagesPerPage').val()));
	console.log("Number of images to display " + this.numImagesToDisplay);
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
			if (!imgEditor.img || img.name != imgEditor.img.name) {
				img.displayCounter = this.displayCounter;
				imgEditor.initialize(this.selectedImageSet, img, this.selectedSite, this.selectedCameraSet);	
		      } else {
		      	if (imgEditor.map) {
		          imgEditor.map.updateSize();
		        }
		      }
			// load existing tie points into the editor state and create features for them someday...					
		} else {
			imgEditor.blank();
		}
		j++;
	}
};

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

EventTriggerCreator.prototype.populateTriggerSelector = function(initialTrigger) {
	this.triggerId = initialTrigger;
	var that = this;
	$.ajax({
		type : "GET",
		url : "/meta/rest/auto/satteleventtrigger",
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

// TODO, need to add ability to draw all triggers once it is has been updated...

EventTriggerCreator.prototype.chooseTrigger = function() {
	triggerIndex = $('#id_trigger_set').val();
	this.triggerId = this.triggers[triggerIndex].id;
	console.log("Trigger " + this.triggerId + " chosen.");
	this.updateSelectedTriggerObject();
}

EventTriggerCreator.prototype.updateSelectedTriggerObject = function() {
	var that = this;
	$.ajax({
		type : "GET",
		url : "/meta/rest/auto/satteleventtrigger",
		data : {
			id : this.triggerId
		},
		success : function(data) {
			that.selectedTriggerSet = data;
		},
		dataType : 'json'
	});
};

EventTriggerCreator.prototype.updateGeometryShape = function(geometryId, newShape, commitToTrigger) {
	var that = this;

	if (that.triggerGeometry != null && geometryId != null) {

		$.ajax({
			type : "POST",
			url : "/apps/event_trigger/update_geometry_polygon",
			data : {
				image_id : that.triggerGeometry.image_id,
				points : newShape,
				sattelgeometryobject_id : geometryId,				
				site_id : that.triggerGeometry.site_id,
				projection_mode : "z_plane",
				height : that.triggerGeometry.height
			},
			success : function(data) {
				alert("Geometry updated");
				if (commitToTrigger) {
					that.addGeometryToTrigger(that.triggerGeometry.type, data);
				}
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

EventTriggerCreator.prototype.updateGeometryHeight = function() {

	// TODO, make this real once there is a height field and once the geometry knows its image_id...
	return;

	var that = this;

	if (that.triggerGeometry != null && that.selectedGeometry != null) {

		$.ajax({
			type : "POST",
			url : "/apps/event_trigger/update_geometry_polygon",
			data : {
				image_id : that.triggerGeometry.image_id,
				points : that.selectedGeometry.points,
				sattelgeometryobject_id : that.selectedGeometry.id,				
				site_id : that.triggerGeometry.site_id,
				projection_mode : "z_plane",
				height : that.triggerGeometry.height
			},
			success : function(data) {
				alert("Geometry height updated");
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

EventTriggerCreator.prototype.addGeometryToTrigger = function(type, geometry) {
	var that = this;
	if (that.selectedTriggerSet) {
		if (type == REFERENCE_TYPE) {
			that.selectedTriggerSet.reference_areas.append(geometry.id);
		} else {
			that.selectedTriggerSet.event_areas.append(geometry.id);
		}

		$.ajax({
			type : "PATCH",
			url : "/meta/rest/auto/satteleventtrigger/",
			data : that.selectedTriggerSet,
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
	var bogus_poly = "POLYGON((0 0 0, 0 0 0, 0 0 0, 0 0 0))"
	var bogus_origin = "POINT(0 0 0)";

	var that = this;
	// Create the polygon, update it, and add it to the trigger
	$.ajax({
		type : "POST",
		url : "/meta/rest/auto/sattelgeometryobject/",
		data : {
			name : this.triggerGeometry.name,
			description : this.triggerGeometry.desc, 
			site : this.triggerGeometry.site_id,
			_attributes : {},
			origin : bogus_origin,
			geometry : bogus_poly
		},
		success : function(data) {
			alert("Geometry Created");

			// Update the geometry shape
			that.updateGeometryShape(data.id, geometryString, true);

			that.setSelectedGeometry(data.id);

			console.log("Saved shape: " + that.triggerGeometry.name + ", desc " + that.triggerGeometry.desc + 
			", imageId " + that.triggerGeometry.image_id + ", points " + that.triggerGeometry.points);

			// TODO, add the geometry object to all of the editors and remove the
			// one drawn...

			that.editComplete();	
		},
		error : function() {
			alert("Unable to create geometry");
		},
		dataType : 'json'
	});
}

EventTriggerCreator.prototype.editEventTriggerGeometry = function(geometryId, geometryString) {
	console.log("Editing trigger geometry...: " + geometryId + ", " + geometryString);
	// TODO wire up update API FOR REGION

	this.editComplete();	
}

EventTriggerCreator.prototype.setSelectedGeometry = function(geometryId) {
	var that = this;
	$.ajax({
		type : "GET",
		url : "/meta/rest/auto/sattelgeometryobject/",
		data : {
			id : geometryId
		},
		success : function(data) {
			that.selectedGeometry = data;
			$('#triggerDetails').html("Selected " + that.selectedGeometry.name + ": " + that.selectedGeometry.description);
		},
		error : function() {
			alert("Unable to create geometry");
		},
		dataType : 'json'
	});
}

EventTriggerCreator.prototype.initializeSiteSelector = function() {
	$('#videoList').html('Sites<br><select id="id_site_set" '+
			'onchange="mainViewer.chooseVideoToDisplay()"><option value="">--------</option></select><br>'); //+
   //    'Camera Set<br><select disabled id="id_camera_set"'+
			// 'onchange="mainViewer.chooseVideoToDisplay($('+"'"+'#id_image_set'+"'"+').val())"><option value="">--------</option></select>');
	for (var i = 0; i < this.sites.length; i++) {
		$('#id_site_set').append($("<option />").val(i).text(this.sites[i].name));
	}
};

EventTriggerCreator.prototype.editComplete = function() {
	this.activeEditor = null;
	this.triggerGeometry = null;
}	

EventTriggerCreator.prototype.initializeTriggerSelector = function() {
	$('#triggerList').html('Triggers<br><select id="id_trigger_set" '+
			'onchange="mainViewer.chooseTrigger()"><option value="">--------</option></select><br>'); //+
   //    'Camera Set<br><select disabled id="id_camera_set"'+
			// 'onchange="mainViewer.chooseVideoToDisplay($('+"'"+'#id_image_set'+"'"+').val())"><option value="">--------</option></select>');
	for (var i = 0; i < this.triggers.length; i++) {
		$('#id_trigger_set').append($("<option />").val(i).text(this.triggers[i].name));
	}

	if (this.triggerId != null) {
		$('#id_trigger_set').val(this.triggerId);
	}
};

EventTriggerCreator.prototype.pullDataAndUpdate = function() {
	var that = this;
	$.ajax({
		type : "GET",
		url : "/meta/rest/auto/sattelsite",
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
			$('#sideControlsContentDiv').hide("slide", {}, 300);
			$('#loadOptions').toggle(false);
			that.activeSelector = null;
		} else {
			$('#loadOptions').toggle(true);
			if (that.activeSelector == null) {
				$('#sideControlsContentDiv').show("slide", {}, 300);
			}
			that.activeSelector = "video";
		}
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
          that.triggerGeometry = null;
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
			that.editEventTriggerProperties(that.selectedGeometry.id, 
				that.selectedGeometry.name, that.selectedGeometry.desc, that.selectedGeometry.height, that.selectedGeometry.type);
		}
	});

	$('#createTriggerSetButton').click(function (e) {
		that.triggerSetDialog.dialog( "open" );
	});

	// Now fetch all of the data
	this.pullDataAndUpdate();
};

EventTriggerCreator.prototype.setActiveEditor = function(editor) {
	this.activeEditor = editor;
}

EventTriggerCreator.prototype.createEventTriggerProperties = function() {
	if (this.activeEditor) {
		this.geometryDialog.dialog( "open" );
	} else {
		alert("No editor has been activated.");
	}
}

EventTriggerCreator.prototype.editEventTriggerProperties = function(geometryId, name, desc, height, type) {	
	// TODO: Make this real someday when we have the API to support it.  Right now we don't.
	//	this.geometryDialog.dialog( "open" );
}

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
	mainViewer.triggerGeometry = {};
	mainViewer.triggerGeometry.name = $('#trigger_name').val();
	mainViewer.triggerGeometry.desc = $('#trigger_desc').val();
	mainViewer.triggerGeometry.image_id = mainViewer.activeEditor.editorState.imageId;
	mainViewer.triggerGeometry.site_id = mainViewer.selectedSite;
	mainViewer.triggerGeometry.image_set_id = mainViewer.selectedImageSet;
	mainViewer.triggerGeometry.trigger_id = mainViewer.triggerId;
	mainViewer.triggerGeometry.height = $('#trigger_height').val();
	var e = document.getElementById("trigger_type");
	mainViewer.triggerGeometry.type = e.options[e.selectedIndex].value;
    mainViewer.geometryDialog.dialog( "close" );
	mainViewer.activeEditor.drawGeometry();	
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
				_attributes : {},
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
