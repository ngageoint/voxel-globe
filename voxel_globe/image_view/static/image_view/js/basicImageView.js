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

  var proj = new ol.proj.Projection({
    code : 'ZOOMIFY',
    units : 'pixels',
    extent : [ 0, 0, imgWidth, imgHeight ]
  });

  //Zoomify image source
  var imgsource = new ol.source.Zoomify({
    url : url,
    size : [ imgWidth, imgHeight ],
    crossOriginKeyword : crossOrigin
  });

  //Creates the actual layer to get rendered, for tiled images
  var bigImageLayer = new ol.layer.Tile({
    source : imgsource,
    minResolution: 2  // TODO
  });

  // Create the vector layer in which to place the Planet banner image
  // for keeping the contract happy
  var iconStyle = new ol.style.Style({
    image: new ol.style.Icon( ({
      src: bannerUrl,
      anchor: [1, 1],
      opacity: 0.8,
    }))
  })

  var feature = new ol.Feature(new ol.geom.Point(imgCenter));
  feature.setStyle(iconStyle);

  var vectorSource = new ol.source.Vector();
  var vectorLayer = new ol.layer.Vector({
    source: vectorSource
  });

  vectorSource.addFeature(feature);

  var littleImageLayer = new ol.layer.Tile({
    source: imgsource,
    maxResolution: 2
  })

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

  this.map.on('postrender', function(e) {  // TODO every frame, not only when done!!
    // get pxl location intersecting with bottom right corner of canvas
    var canvas_width = $("#" + that.divName).width();
    var canvas_height = $("#" + that.divName).height();
    var pixel = [canvas_width, canvas_height];  // bottom right hand corner

    var coordinate = e.map.getCoordinateFromPixel(pixel);
    // set feature's position to that location
    feature.setGeometry(new ol.geom.Point(coordinate));

    if (!littleImageLayer.getExtent()){
      setExtent();
    }
  })

  function setExtent() {
    var fullExtent = that.map.getView().calculateExtent(that.map.getSize());
    var restrictedExtent = fullExtent.map(function(x) { return x / 20 });  //TODO restrict to 1 square km
    that.map.getView().setCenter(ol.extent.getCenter(restrictedExtent));
    console.log(fullExtent);
    console.log(restrictedExtent);
    littleImageLayer.setExtent(restrictedExtent);
  }
}
