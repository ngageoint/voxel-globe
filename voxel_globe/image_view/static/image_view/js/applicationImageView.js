function ImageViewMain() {
  this.imageSets = [];
  this.images = [];
  this.paginator;
  this.imageEditors = [];
  this.numImagesToDisplay = 1;
  this.displayingImage = 0;
  this.imageWidths = [ 99, 49, 32, 24, 24, 24, 24, 24 ];
  this.imageHeights = [ 99, 99, 99, 99, 49, 49, 49, 49 ];
}

ImageViewMain.prototype.init = function() {
  var that = this;
  this.initializeSlideout();
  this.initializeImageSelector();
  this.paginator = new Paginator({div : "paginator", id : "1"});
  
  for (var i = 0; i < 8; i++) {
    var imgEditor = new BasicImagePane("imageContainer", i);
    this.imageEditors.push(imgEditor);
  }

  $('#numImagesPerPage').change(function(e) {   
    var num = parseInt($.trim($('#numImagesPerPage').val()));
    if (num >= 1 && num <= 8) {
      that.updateLayout();
    }
  });
}

ImageViewMain.prototype.initializeSlideout = function() {
  this.slidOut = true;
  var that = this;
  $('#loadImageSet').mousedown(function(e) {
    if (that.slidOut) {
      $('.slideout-content').hide("slide", {}, 300);
      that.slidOut = false;
    } else {
      $('.slideout-content').show("slide", {}, 300);
      that.slidOut = true;
    }
  });
}

ImageViewMain.prototype.updateLayout = function() {
  this.numImagesToDisplay = parseInt($.trim($('#numImagesPerPage').val()));
  console.log("Number of images to display " + this.numImagesToDisplay);
  for (var i = this.numImagesToDisplay; i < this.imageEditors.length; i++) {
    this.imageEditors[i].hide();
  }
  var width = this.imageWidths[this.numImagesToDisplay - 1];
  var height = this.imageHeights[this.numImagesToDisplay - 1];

  for (var i = 0; i < this.numImagesToDisplay; i++) {
    this.imageEditors[i].show(width, height);
  }
  this.paginator.initialize(this.images.length, this.numImagesToDisplay, 
      this.displayingImage, displayImage);
};

ImageViewMain.prototype.initializeImageSelector = function() {
  var that = this;
  $.ajax({
    type : "GET",
    url : "/meta/rest/auto/imageset",
    data : {},
    success : function(data) {
      that.imageSets = data;
      if (that.imageSets.length > 0) {
        for (var i = 0; i < that.imageSets.length; i++) {
          $('#id_image_set').append($("<option />")
            .val(i).text(that.imageSets[i].name));
        }
      } else {
        $('#imageSetList').html("No image sets found in the database.");
      }
    },
    dataType : 'json'
  });

  $('#id_image_set').on('change', function() {
    that.displayImageSet(this.value);
  });
};

ImageViewMain.prototype.displayImageSet = function(imageSet) {
  this.imageSet = this.imageSets[imageSet].id;
  if (imageSet == '') {
    $('#imageStatus').html("");
    return;
  }

  var that = this;

  $.ajax({
    type : "GET",
    url : "/meta/rest/auto/image",
    data : {
      imageset : that.imageSets[imageSet].id
    },
    success : function(data) {
      // Toggle all other image selection buttons
      if (data.error) {
        alert(data.error);
      } else { 
        that.images = data;
        if (that.images.length > 0) {
          that.initializeImageSet();
        } else {
          console.log(that);
          for (ed of that.imageEditors) {
            ed.blank();
          }
          $('#imageStatus').html("No images found in the database.");
        }
      }
    },
    dataType : 'json'
  });
}

ImageViewMain.prototype.initializeImageSet = function() {
  $('#imageStatus').html("Click and drag to pan<br>" + 
      "Scroll to zoom<br>Alt + Shift + drag to rotate<br>");
  $('#numImagesPerPage').val(1);
  this.updateLayout();
  this.paginator.initialize(this.images.length, 1, 0, displayImage);
  $('#numDisplay').css('display', 'inline-block');
  if (this.images.length > 1) {
    this.paginator.show();
    $("#numDisplay").show();
  } else {
    this.paginator.hide();
    $("#numDisplay").hide();
  }
}

ImageViewMain.prototype.displayImage = function(i) {
  var that = this;
  // var img = this.images[i];
  this.displayingImage = i;
  var j = i;

  for (i = 0; i < this.numImagesToDisplay; i++) {
    var imgEditor = this.imageEditors[i];
    var img = this.images[j];
    if (img) {
      if (!imgEditor.img || img.name != imgEditor.img.name) {
        imgEditor.initialize(img, this.imageSet);
      } else {
        if (imgEditor.map) {
          imgEditor.map.updateSize();
        }
      }
    } else {
      imgEditor.blank();
    }
    j++;
  }
}

var mainViewer = new ImageViewMain();
$(document).ready(function() {
  mainViewer.init();
});

function displayImage(imgNdx) {
  mainViewer.displayImage(imgNdx);
}





function BasicImagePane(imageContainerDivName, editorCount) {
  this.divName = "imageWrapper" + editorCount;
  this.imageDivName = "image" + editorCount;
  this.toolbarDivName = "imageToolbar" + editorCount;
  this.imageNameField = "imageName" + editorCount;
  this.editorId = editorCount;
  this.isInitializing = false;
  this.img = null; 
  this.imageEditor = null;   
  this.map = null;

  var divText = '<div id="' + this.divName
      + '" class="imageWidget"><div id="' + this.imageDivName
      + '" class="imageContents"></div><div id="' + this.toolbarDivName
      + '" class="imageToolbar"></div></div>';
  $('#' + imageContainerDivName).append(divText);
}

BasicImagePane.prototype.initialize = function(img, imageSet) {
  if (this.isInitialzing) {
    return;
  }
  this.isInitializing = true;
  console.log("Initializing image " + img.name);
  $('#' + this.imageDivName).html("");
  $('#' + this.toolbarDivName).html("");
  $('#' + this.toolbarDivName).toggle(true);
  this.imageEditor = new ImageViewer(this.imageDivName, img, null, imageSet);
  this.img = img;
  this.map = this.imageEditor.map;
  this.isInitializing = false;
}

BasicImagePane.prototype.blank = function() {
  this.img = null;
  this.isInitializing = false;
  if (this.imageEditor) {
    this.imageEditor.blank();
  }
  $('#' + this.toolbarDivName).toggle(false);
}

BasicImagePane.prototype.show = function(width, height) {
  $('#' + this.divName).css("height", height + '%');
  $('#' + this.divName).css("width", width + '%');
  $('#' + this.divName).toggle(true);
}

BasicImagePane.prototype.hide = function() {
  $('#' + this.divName).toggle(false);
  this.blank();
}