function ImageViewer(imageDivName, img) {
  this.divName = imageDivName;
  this.imgWidth = img.width;
  this.imgHeight = img.height;
  this.imgUrl = img.url;
  this.img = img;
  this.imgName = img.name;

  $('#' + this.divName).html('');
  $('#' + this.divName).append('<div class="imgBanner">' + 
    '<img src="' + iconFolderUrl + 'planet.svg">' + 
    '<div class="p1">Includes material ©2016 Planet Labs Inc. All rights reserved.</div>' +
    '<div class="p2">DISTRIBUTION STATEMENT C: Distribution authorized to U.S. Government Agencies and their contractors (Administrative or Operational Use) Other requests for this document shall be referred to AFRL, Wright-Patterson Air Force Base, OH 45433-7321.</div></div>')
  $(".imgBanner").css('display', 'block');

  var imgWidth = this.imgWidth;
  var imgHeight = this.imgHeight;
  var url = this.imgUrl;
  var crossOrigin = 'anonymous';
  var that = this;
  var imgCenter = [ imgWidth / 2, -imgHeight / 2 ];

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
  var imgtile = new ol.layer.Tile({
    source : imgsource
  });

  this.map = new ol.Map({
    interactions : ol.interaction.defaults(),
    layers : [ imgtile ],
    target : this.divName,
    controls : [], // Disable default controls
    view : new ol.View({
      projection : proj,
      center : imgCenter,
      zoom : 1
    })
  });

  setInterval(function(){
    console.log('Resolution: ' + that.map.getView().getResolution());
    console.log('Width of viewer: ' + $("#" + that.divName).width());
    console.log('Height of viewer: ' + $("#" + that.divName).height());
  }, 3000);
}