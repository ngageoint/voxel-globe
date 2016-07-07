function ImageViewer(imageDivName, img) {
  this.divName = imageDivName;
  this.img = img;
  var that = this;
  $('#' + this.divName).html('');

  var imgWidth = this.img.width;
  var imgHeight = this.img.height;
  var imgCenter = [ imgWidth / 2, -imgHeight / 2 ];
  var url = this.img.url;
  var crossOrigin = 'anonymous';
  var gsd = 10;
  // TODO the above gsd is just for example; from metadata, get the real gsd
  var fullSizeMaxGsd = 30;
  var cutoffResolution = gsd / fullSizeMaxGsd;  //TODO this is prob wrong
  var imgWidthMeters = gsd * imgWidth;
  var imgHeightMeters = gsd * imgHeight;
  var originalClipSize = 1000 / gsd;
  var bigImageMaxZoom;

  // Create a 'fake' projection for the openlayers map to use
  var proj = new ol.proj.Projection({
    code : 'ZOOMIFY',
    units : 'pixels',
    extent : [ 0, 0, imgWidth, imgHeight ]
  });

  // Zoomify image source
  var imgsource = new ol.source.Zoomify({
    url : url,
    size : [ imgWidth, imgHeight ],
    crossOriginKeyword : crossOrigin
  });

  // Create the big image layer, visible when zoomed all the way out
  var bigImageLayer = new ol.layer.Tile({
    source : imgsource,
    minResolution: cutoffResolution
  });

  // Layer that restricts the image size at higher resolutions
  // (keepin the contract happy)
  var littleImageLayer = new ol.layer.Tile({
    source: imgsource,
    maxResolution: cutoffResolution
  })

  // Vector layer for the planet logo and distribution statement
  var vectorLayer = new ol.layer.Vector({
    source: new ol.source.Vector()
  });

  // Create the map itself
  this.map = new ol.Map({
    interactions : ol.interaction.defaults(),
    layers : [ bigImageLayer, littleImageLayer, vectorLayer ],
    target : this.divName,
    controls : [], // Disable default controls
    view : new ol.View({
      projection : proj,
      center : imgCenter,
      zoom : 1,
      extent: [0, -imgHeight, imgWidth, 0]
    })
  });

  if (true) {  // TODO if it's a planet labs image
    var img = document.getElementById("imgBanner");
    img.style.display = "block";
    
    // Affix planet logo and distribution statement to bottom right of canvas
    vectorLayer.on('precompose', function(event) {
      var ctx = event.context;
      ctx.save();
      var canvas_width = $("#" + that.divName).width();
      var canvas_height = $("#" + that.divName).height();
      var img_width = img.clientWidth;
      var img_height = img.clientHeight;
      var x = canvas_width - img_width;
      var y = canvas_height - img_height;
      ctx.globalAlpha = 0.8;
      ctx.drawImage(img, x, y);
      ctx.globalAlpha = 1;
    });

    vectorLayer.on('postcompose', function(event) {
      var ctx = event.context;
      ctx.restore();
    })

    // Restrict the visible window of the image when zoomed to a high res
    littleImageLayer.on('precompose', function(event) {
      var clipSize = getClipSize();
      var ctx = event.context;
      ctx.save();
      var pixelRatio = event.frameState.pixelRatio;
      var size = that.map.getSize();
      ctx.translate(size[0] / 2 * pixelRatio, size[1] / 2 * pixelRatio);
      ctx.translate(-clipSize / 2, -clipSize / 2);
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(clipSize, 0);
      ctx.lineTo(clipSize, clipSize);
      ctx.lineTo(0, clipSize);
      ctx.clip();
      ctx.translate(clipSize / 2, clipSize / 2);
      ctx.translate(-size[0] / 2 * pixelRatio, -size[1] / 2 * pixelRatio);
    });

    littleImageLayer.on('postcompose', function(event) {
      var ctx = event.context;
      ctx.restore();
    });

    function getClipSize() {  // TODO this is super wrong
      // var clipSizeMeters = 1000;
      // var currentResolution = that.map.getView().getResolution();
      // var imgWidthPixels = imgWidth * currentResolution;
      // var currentGSD = imgWidthMeters / imgWidthPixels;
      // var clipSizePixels = clipSizeMeters / currentGSD;
      // return clipSizePixels;

      var currentResolution = that.map.getView().getResolution();
      var currentClipSize = originalClipSize / currentResolution;
      return currentClipSize;
    }
  }
}

ImageViewer.prototype.blank = function() {
  $("#" + this.divName).html('');
}
