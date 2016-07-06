function ImageViewMain() {
  this.imageSets = [];
  this.images = [];
  this.paginator;
  this.imageEditor;
}

ImageViewMain.prototype.init = function() {
  this.initializeSlideout();
  this.initializeImageSelector();
  this.paginator = new Paginator({div : "paginator", id : "1"});
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

ImageViewMain.prototype.initializeImageSelector = function() {
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
        that.imageSets.push(img);
      }
      if (that.imageSets.length > 0) {
        for (var i = 0; i < that.imageSets.length; i++) {
          $('#id_image_set').append($("<option />").val(i).text(that.imageSets[i].name));
        }
      } else {
        $('#imageSetList').html("No images found in the database.");
      }
    },
    dataType : 'json'
  });

  $('#id_image_set').on('change', function() {
    that.displayImageSet(this.value);
  });
};

ImageViewMain.prototype.displayImageSet = function(imageSet) {
  if (imageSet == '') {
    $('#imageStatus').html("");
    return;
  }

  var images = [];
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
        for (var i = 0; i < data.length; i++) {
          var img = {
            id : data[i].id,
            name : data[i].name,
            url : data[i].zoomify_url,
            width : data[i].image_width,
            height : data[i].image_height
          };
          images.push(img);
        }

        if (images.length > 0) {
          that.initializeImageSet(images);
        } else {
          $('#imageStatus').html("No images found in the database.");
        }
      }
    },
    dataType : 'json'
  });
}

ImageViewMain.prototype.initializeImageSet = function(images) {
  this.images = images;
  $('#imageStatus').html("Click and drag to pan<br>Scroll to zoom<br>Alt + Shift + drag to rotate<br>");
  this.paginator.initialize(this.images.length, 1, 0, displayImage);
}

ImageViewMain.prototype.displayImage = function(i) {
  var img = this.images[i];
  console.log('Displaying ' + img.name);
  this.displayingImage = i;

  if (img) {
    this.imageEditor = new ImageViewer("imageContainer", this.images[i]);
  } else {
    // TODO this.imageEditor.blank();
  }
}

ImageViewMain.prototype.incrementImageInitialized = function() {}

var mainViewer = new ImageViewMain();
$(document).ready(function() {
  mainViewer.init();
});

function displayImage(imgNdx) {
  mainViewer.displayImage(imgNdx);
}