var timeout;
var ACTIVE_COLOR = 'rgba(255, 255, 0, 0.9)';
var INACTIVE_COLOR = 'rgba(119, 204, 255, 0.75)';

/**
 * This class supports the overall UI layout and data.
 */
function EventTriggerCreator() {
	this.imageEditors = [];
	this.videos = [];
	this.images = [];
	this.numImagesToDisplay = 1;
	this.displayingImage = 0;
	this.selectedVideo = -1;
	this.imageWidths = [ 99, 49, 32, 24 ];
	this.imageHeights = [ 99, 99, 99, 99 ];
	this.bannerScale = [ 100, 90, 80, 70];
	this.configurationAction = null;
	
	this.activeImageEditor = null;
	this.editedControlPoint = null;
	this.displayCounter = 0;
	this.visibleImageCounter = 0;
	this.initializedImageCounter = 0;
}

EventTriggerCreator.prototype.updateLayout = function() {
	this.numImagesToDisplay = parseInt($.trim($('#numImagesPerPage').val()));
	console.log("Number of images to display " + this.numImagesToDisplay);
	for (var i = 0; i < this.imageEditors.length; i++) {
		this.imageEditors[i].hide();
	}
	var width = this.imageWidths[this.numImagesToDisplay - 1];
	var height = this.imageHeights[this.numImagesToDisplay - 1];
	var scale = this.bannerScale[this.numImagesToDisplay - 1];

	for (var i = 0; i < this.numImagesToDisplay; i++) {
		this.imageEditors[i].show(width, height, scale);
	}
	this.displayImage(0);
};

EventTriggerCreator.prototype.displayImage = function(imgNdx) {
	console.log("Displaying image " + imgNdx);
	$('#selectImgControlPoints').prop("disabled","disabled"); // disable it until control points are loaded
	this.displayCounter++;

	var that = this;
	var j = imgNdx;
	this.initializedImageCounter = 0;
	for (var i = 0; i < this.numImagesToDisplay; i++) {
		var imgEditor = this.imageEditors[i];
		var img = this.images[j];
		if (img) {
			var that = this;
			// load existing tie points into the editor state and create features for them someday...
			img.displayCounter = this.displayCounter;
			imgEditor.initialize(img);			
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

}

EventTriggerCreator.prototype.chooseVideoToDisplay = function(videoNdx) {
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
			imageset : that.videos[videoNdx].id
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
						url : data[i].zoomify_url,
						width : data[i].image_width,
						height : data[i].image_height
					};
					that.images.push(img);
				}
				if (that.images.length > 0) {
					that.displayImage(0);
				} else {
					$('#imageWidget').html("No images found in the database.");
				}
			}
		},
		dataType : 'json'
	});

};

EventTriggerCreator.prototype.loadCameraSets = function() {
	$('#id_camera_set').prop('disabled', true);
	$('#id_camera_set option[value!=""]').remove();
	videoNdx = $('#id_image_set').val();
	console.log(videoNdx);
	var that = this;
	$.ajax({
		type : "GET",
		url : "/meta/rest/auto/cameraset/",
		data : {
			images : that.videos[videoNdx].id
		},
		success : function(data) {
			for (var i = 0; i< data.length; i++) {
				$('#id_camera_set').append($("<option />").val(data[i].id).text(data[i].name));
			}
			$('#id_camera_set').prop('disabled', false)
		},
		dataType : 'json'
	});
}

EventTriggerCreator.prototype.initializeVideoSelector = function() {
	$('#videoList').html('Image Set<br><select id="id_image_set"'+
			'onchange="mainViewer.loadCameraSets()"><option value="">--------</option></select><br>'+
      'Camera Set<br><select disabled id="id_camera_set"'+
			'onchange="mainViewer.chooseVideoToDisplay($('+"'"+'#id_image_set'+"'"+').val())"><option value="">--------</option></select>');
	for (var i = 0; i < this.videos.length; i++) {
		$('#id_image_set').append($("<option />").val(i).text(this.videos[i].name));
	}
};

EventTriggerCreator.prototype.pullDataAndUpdate = function() {
	var that = this;
	$.ajax({
		type : "GET",
		url : "/meta/rest/auto/imageset",
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
};

EventTriggerCreator.prototype.initializeDataAndEvents = function() {

	for (var i = 0; i < 8; i++) {
		var imgEditor = new EventTriggerEditor("imageContainer", i);
		this.imageEditors.push(imgEditor);
	}
	
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

	$('#videoSelectionOptions').toggle(true);
	$('#sideControlsContentDiv').toggle(true);
	this.activeSelector = "video";

	$('#videoList').html("Downloading video list...");
	$('#controlPointList').html("Downloading control point list...");

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
			$('#videoSelectionOptions').toggle(false);
			that.activeSelector = null;
		} else {
			$('#videoSelectionOptions').toggle(true);
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
	
	// Now fetch all of the data
	this.pullDataAndUpdate();
};

function refreshDisplay() {
	
}


