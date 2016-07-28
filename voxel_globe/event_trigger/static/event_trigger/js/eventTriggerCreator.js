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
	this.imageWidths = [ 99, 49, 32, 24 ];
	this.imageHeights = [ 100, 100, 100, 100 ];
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
	// this.displayImage(0);
	this.imagePaginator.initialize(this.images.length, this.numImagesToDisplay, this.displayingImage, displayImage);
};

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
			var that = this;
			// load existing tie points into the editor state and create features for them someday...
			img.displayCounter = this.displayCounter;
			imgEditor.initialize(this.selectedImageSet, img, this.selectedSite);			
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
					that.imagePaginator.initialize(that.images.length, that.numImagesToDisplay, 0, displayImage);
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
};

EventTriggerCreator.prototype.initializeSiteSelector = function() {
	$('#videoList').html('Sites<br><select id="id_site_set"'+
			'onchange="mainViewer.chooseVideoToDisplay()"><option value="">--------</option></select><br>'); //+
   //    'Camera Set<br><select disabled id="id_camera_set"'+
			// 'onchange="mainViewer.chooseVideoToDisplay($('+"'"+'#id_image_set'+"'"+').val())"><option value="">--------</option></select>');
	for (var i = 0; i < this.sites.length; i++) {
		$('#id_site_set').append($("<option />").val(i).text(this.sites[i].name));
	}
};

EventTriggerCreator.prototype.pullDataAndUpdate = function() {
	var that = this;
	$.ajax({
		type : "GET",
		url : "/meta/rest/auto/sattelsite",
		data : {},
		success : function(data) {
			for (var i = 0; i < data.length; i++) {
				var site = {
					id : data[i].id,
					name : data[i].name,
					image_set : data[i].image_set,
					camera_set : data[i].camera_set
				};
				that.sites.push(site);
			}
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
		var imgEditor = new EventTriggerEditor("imageContainer", i);
		this.imageEditors.push(imgEditor);
	}
	this.imagePaginator = new Paginator({div : "paginator", id : "1"});
	
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

	this.imagePaginator.initialize(0, this.numImagesToDisplay, this.displayingImage, new function() {});

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
	// for (var i = 0; i < mainViewer.imageEditors.length; i++) {
	// 	mainViewer.imageEditors[i].resize();
	// }
	mainViewer.displayImage(0);
}

function displayImage(imgNdx) {
	mainViewer.displayImage(imgNdx);
}

