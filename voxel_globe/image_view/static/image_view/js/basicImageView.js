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
    minResolution: 2  // TODO
  });

  // Layer that restricts the image size at higher resolutions
  // (keepin the contract happy)
  var littleImageLayer = new ol.layer.Tile({
    source: imgsource,
    maxResolution: 2  // TODO
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
      zoom : 1
    })
  });

  if (true) {  // TODO if it's a planet labs image
    // Affix planet logo and distribution statement to bottom right of canvas
    vectorLayer.on('precompose', function(event) {
      var ctx = event.context;
      ctx.save();
      var img = document.getElementById("imgBanner");
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
      var ctx = event.context;
      ctx.save();
      var pixelRatio = event.frameState.pixelRatio;
      var size = that.map.getSize();
      ctx.translate(size[0] / 2 * pixelRatio, size[1] / 2 * pixelRatio);
      ctx.scale(3 * pixelRatio, 3 * pixelRatio);
      ctx.translate(-60, -60);  //TODO
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(120, 0);
      ctx.lineTo(120, 120);
      ctx.lineTo(0, 120);
      ctx.clip();
      ctx.translate(60, 60);
      ctx.scale(1 / 3 / pixelRatio, 1 / 3 / pixelRatio);
      ctx.translate(-size[0] / 2 * pixelRatio, -size[1] / 2 * pixelRatio);
    });

    littleImageLayer.on('postcompose', function(event) {
      var ctx = event.context;
      ctx.restore();
    });
  }
}
