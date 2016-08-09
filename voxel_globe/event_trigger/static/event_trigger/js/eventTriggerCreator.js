var timeout;
var ACTIVE_COLOR = 'rgba(255, 255, 0, 0.9)';
var INACTIVE_COLOR = 'rgba(119, 204, 255, 0.75)';
var NUM_EDITORS = 4;

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

	this.editedTriggerSet = null;
	this.editedTrigger = null;
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

	this.populateTriggerSelector();
};

EventTriggerCreator.prototype.populateTriggerSelector = function() {
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

EventTriggerCreator.prototype.chooseTrigger = function() {
	triggerIndex = $('#id_trigger_set').val();
	this.triggerId = this.triggers[triggerIndex].id;
	console.log("Trigger " + this.triggerId + " chosen.");
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
	for (var i = 0; i < this.triggers.length; i++) {
		$('#id_trigger_set').append($("<option />").val(i).text(this.triggers[i].name));
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
	
	this.dialog = $( "#triggerFormDiv" ).dialog({
	  autoOpen: false,
      width: 550,
      modal: true,
      buttons: {
        "OK": saveTriggerFormProperties,
        Cancel: function() {
          that.dialog.dialog( "close" );
          that.editedTrigger = null;
        }
      },
      close: function() {
        that.form[ 0 ].reset();
      }
  	});

  	this.form = this.dialog.find( "form" ).on( "submit", function( event ) {
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
          this.triggerSetDialog.dialog( "close" );
        }
      },
      close: function() {
        that.triggerSetForm[ 0 ].reset();
      }
  	});

  	this.triggerSetForm = this.dialog.find( "form" ).on( "submit", function( event ) {
      event.preventDefault();
      createTriggerSet();
    });
	
	$('#editTriggerProperties').click(function (e) {
		that.selectRegion(0); // TODO, hook into selection...
		that.editEventTriggerProperties(that.selectedRegion.id, 
			that.selectedRegion.name, that.selectedRegion.desc, that.selectedRegion.height, that.selectedRegion.type);
	});

	$('#createTriggerSetButton').click(function (e) {
		that.triggerSetDialog.dialog( "open" );
	});

	// Now fetch all of the data
	this.pullDataAndUpdate();
};

EventTriggerCreator.prototype.createEventTriggerProperties = function(activeEditor, imageId) {

	console.log("Setting field: " + imageId);

	$('#trigger_region_id').val("");
	$('#trigger_image_id').val(imageId);
	$('#trigger_shape_str').val("");
	$('#trigger_type').prop("disabled", "");
	this.activeEditor = activeEditor;

	this.dialog.dialog( "open" );
}

EventTriggerCreator.prototype.editComplete = function() {
	this.activeEditor = null;
	this.editedTrigger = null;
}

EventTriggerCreator.prototype.createEventTrigger = function(regionString) {
	console.log("Saving shape: " + this.editedTrigger.name + ", desc " + this.editedTrigger.desc + 
		", imageId " + this.editedTrigger.image_id + ", points " + this.editedTrigger.points);

	this.editComplete();	
}


EventTriggerCreator.prototype.editEventTriggerRegion = function(regionId, regionString) {
	console.log("Editing trigger region...: " + regionId + ", " + regionString);
	// TODO wire up update API FOR REGION

	this.editComplete();	
}

EventTriggerCreator.prototype.selectRegion = function(regionId) {
	// TODO, look up regions by id and populate all of the relevant values...
	this.selectedRegion = {
		id : 999,
		name : "foo2",
		desc : "fake description",
		type : "REFERENCE",
		height : 10
	};
}

EventTriggerCreator.prototype.editEventTriggerProperties = function(regionId, name, desc, height, type) {

	console.log("Setting field: " + name + ", " + desc + ", " + height);

	$('#trigger_region_id').val(regionId);
	$('#trigger_name').val(name);
	$('#trigger_desc').val(desc);
	$('#trigger_image_id').val("");
	$('#trigger_shape_str').val("");
	$('#trigger_height').val(height);
	//$("#trigger_type option[value='"+ type +"']").attr('selected', 'selected');
	$("#trigger_type").val(type);
	$('#trigger_type').prop("disabled", "disabled");

	this.dialog.dialog( "open" );

	// TODO API FOR UPDATING PROPERTIES
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
	mainViewer.editedTrigger = {};
	mainViewer.editedTrigger.name = $('#trigger_name').val();
	mainViewer.editedTrigger.desc = $('#trigger_desc').val();
	mainViewer.editedTrigger.image_id = $('#trigger_image_id').val();
	mainViewer.editedTrigger.site_id = mainViewer.selectedSite;
	mainViewer.editedTrigger.image_set_id = mainViewer.selectedImageSet;
	mainViewer.editedTrigger.points = $('#trigger_shape_str').val();
	mainViewer.editedTrigger.height = $('#trigger_height').val();
	var e = document.getElementById("trigger_type");
	mainViewer.editedTrigger.type = e.options[e.selectedIndex].value;

	// TODO add a field for the main event trigger set

    mainViewer.dialog.dialog( "close" );
	mainViewer.activeEditor.drawRegion();
	
}

function createTriggerSet() {
	var name = $('#trigger_set_name').val();
	var desc = $('#trigger_set_desc').val();
	var site_id = mainViewer.selectedSite;
	var bogus_origin = "POINT(0 0 0)";
	var bogus_ref_img = mainViewer.images[0].id;
	//var bogus_poly = "POLYGON((0 0,0 0, 0 0, 0 0))"

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
				mainViewer.populateTriggerSelector();
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
