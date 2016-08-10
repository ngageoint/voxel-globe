function ImageViewer(imageDivName, img, cameraSet, imageSet) {
  this.divName = imageDivName;
  this.img = img;
  this.cameraSet = cameraSet;
  this.imageSet = imageSet;

  this.imgWidth = this.img.image_width;
  this.imgHeight = this.img.image_height;
  this.imgCenter = [this.imgWidth / 2, -this.imgHeight / 2 ];

  // default values
  this.gsd = 2.6;
  this.up_rotation = 0;
  this.north_rotation = 0;

  // clear div
  $('#' + this.divName).html('');

  // Create an empty map 
  this.map = new ol.Map({
    interactions : ol.interaction.defaults({
      DragRotate: false
    }),
    target : this.divName,
    controls : [], // Disable default controls
    view : new ol.View({
      projection : new ol.proj.Projection({
          code : 'ZOOMIFY',
          units : 'pixels',
          extent : [ 0, 0, this.imgWidth, this.imgHeight ]
        }),
      center : this.imgCenter,
      zoom : 1,
      //extent: [0, -this.imgHeight, this.imgWidth, 0]
    })
  });

  // populate map  
  this.getImageInfo();

  this.map.imgCenter = this.imgCenter;

}

ImageViewer.prototype.getImageInfo = function() {
  var that = this;
  var cameraSet = that.cameraSet;
  var imageSet = that.imageSet;

  if (!cameraSet && !imageSet) {
    console.log('Unable to load gsd and up directions for the image.')
    this.createMap();
    return;
  }

  // pull down additional image info to get north-is-up, gsd, etc.
  if (!cameraSet) {
    $.when(
      $.ajax({
        type: "GET",
        url: "/meta/rest/auto/cameraset/",
        data: {
          images: imageSet
        },
        success: function(data) {
          cameraSet = data[0].id;
        }
      })
    ).then(function() {
      requestImageInfo(that.img.id, cameraSet);
    });
  } else {
    requestImageInfo(that.img.id, cameraSet);
  }

  function requestImageInfo(i, c) {
    return $.ajax({
      type: "GET",
      url: "/meta/get_additional_image_info/" + i + "/" + c,
      success: function(data) {
        data = JSON.parse(data);
        if (data.up_rotation) {
          that.up_rotation = data.up_rotation;
        }
        if (data.north_rotation) {
          that.north_rotation = data.north_rotation;
        }
        if (data.gsd) {
          that.gsd = data.gsd;
        }
        that.createMap();
            console.log('creating map')
      }
    });
  }
}

ImageViewer.prototype.createMap = function() {
  var that = this;
  // console.log(that);

  // debugging
  // console.log(that.img.name,'| GSD: ',that.gsd);

  // check for planet imagery (delivered with image data)
  var tf_planet = that.img.hasOwnProperty('_attributes') && 
     that.img._attributes.includes('planet_rest_response');
      
  // basic image layer
  if (!tf_planet) {
    
    // create one image layer
    var imageLayer = new ol.layer.Tile({
      source: new ol.source.Zoomify({
        url : that.img.zoomify_url,
        size : [ that.imgWidth, that.imgHeight ],
        crossOriginKeyword : 'anonymous',
      }),
    }); 
    imageLayer.setZIndex(-1);

    that.map.addLayer(imageLayer);


  // Planet Labs image 
  } else {

    // limiting factors
    var cutoffResolution = 30 / this.gsd;
    var originalClipSize = 1000 / this.gsd;


    // BACKGROUND IMAGE LAYER: limited by fullSizeMaxGSD

    // zoomify source
    var backgroundSource = new ol.source.Zoomify({
      url : that.img.zoomify_url,
      size : [ that.imgWidth, that.imgHeight ],
      crossOriginKeyword : 'anonymous',
    });

    // limit source by maxzoom
    var resolutions = backgroundSource.tileGrid.getResolutions();
    var maxzoom = 0;
    for (var k = 0; k < resolutions.length; k++) {
      if (resolutions[k] >= cutoffResolution) {
        maxzoom = k;
      } else {
        break;
      }
    }
    backgroundSource.tileGrid.maxZoom = maxzoom;

    // add layer to layer array
    var backgroundLayer = new ol.layer.Tile({
      source: backgroundSource,
    }); 
    backgroundLayer.setZIndex(-2);
    that.map.addLayer(backgroundLayer);


    // CROPPED IMAGE LAYER: limited by originalClipSize

    // image layer
    var cropLayer = new ol.layer.Tile({
      source: new ol.source.Zoomify({
        url : that.img.zoomify_url,
        size : [ that.imgWidth, that.imgHeight ],
        crossOriginKeyword : 'anonymous',
      }),
    });
    cropLayer.setZIndex(-1);

    // mouse position from div
    var mousePosition = null;
    var container = document.getElementById(that.divName);

    container.addEventListener('mousemove', function(event) {
      mousePosition = that.map.getEventPixel(event);
      that.map.render();
    });

    container.addEventListener('mouseout', function(event) {
      mousePosition = null;
      that.map.render();
    });  

    // Restrict the visible window of the image when zoomed to a high res
    cropLayer.on('precompose', function(event) {
      var ctx = event.context;
      ctx.save();
      
      // preferred over "that.map.getView().getResolution()", as viewState
      // contains the exact resolution during a zoom animation
      var currentResolution = event.frameState.viewState.resolution;
      var clipSize = originalClipSize / currentResolution;
      var size = that.map.getSize();
      var pixelRatio = event.frameState.pixelRatio;

      var x,y;
      if (mousePosition) {
        x = mousePosition[0] - (clipSize / 2);
        y = mousePosition[1] - (clipSize / 2);
      } else {
        x = ((size[0]/pixelRatio) - clipSize) / 2;
        y = ((size[1]/pixelRatio) - clipSize) / 2;
      }

      ctx.beginPath();
      ctx.rect(x,y,clipSize,clipSize)
      ctx.clip();      
    });

    cropLayer.on('postcompose', function(event) {
      var ctx = event.context;
      ctx.restore();
    });

    // add completed layer to layer array
    that.map.addLayer(cropLayer);


    // ATTRIBUTION LAYER: overlay planet attribution/distribution statement

    // Vector layer for attribution
    var attributionLayer = new ol.layer.Vector({
      source: new ol.source.Vector()
    });

    // initialize attribution data
    var attributionData = {
        'divName':that.divName,
        'image':loadAttributionImage(attributionMode),
        'mode':attributionMode,
        'location':attributionLocation
    };
    attributionLayer.planetAttributionData = attributionData;
    attributionLayer.setZIndex(99);
    
    // Affix attribution to canvas
    attributionLayer.on('precompose', function(event) {
      var ctx = event.context;
      ctx.save();
      displayAttribution(ctx,this.planetAttributionData);
    });

    attributionLayer.on('postcompose', function(event) {
      var ctx = event.context;
      ctx.restore();
    })

    // add completed layer to layer array
    that.map.addLayer(attributionLayer);

  }

  // rotation control panel
  new RotationControlPanel(that.map, 'topright', that.up_rotation, 
    that.north_rotation);

  // update map size
  //that.map.updateSize();
  
}


ImageViewer.prototype.blank = function() {
  $("#" + this.divName).html('');
}




function loadAttributionImage(mode) {    
  var img = new Image();
  img.onload = function() {
    console.log('ATTRIBUTION IMAGE LOADED');
  }

  switch (mode) {
    case "old":
    img.src = attributionFolderUrl + "banner.png";
    break;
    default:
    img.src = attributionFolderUrl + "planet.svg";
  }
  return img;
}

function displayAttribution(context,attributionData) {    
  switch (attributionData.mode) {
    case 'large':
    largeAttribution(context,attributionData);
    break;
    case 'small':
    smallAttribution(context,attributionData);
    break;
    default:
    oldAttribution(context,attributionData);
  }    
}

function oldAttribution(context,data) {

  var img_width = data.image.width;
  var img_height = data.image.height;

  var pos = getLeftTop(data.divName,data.location,img_width,img_height);

  context.globalAlpha = 0.8;
  context.drawImage(data.image, pos.left, pos.top, img_width, img_height);
  context.globalAlpha = 1;    
}

function smallAttribution(context,data) {

  // sizing parameters
  var fontsize = 10; //pixels
  var margin = 3;
  var lineheight = 2+fontsize;
  
  // attribution statement
  var attribution = "Distribution Statement C \u00B7 Imagery \u00A92016 Planet \u00B7 All rights reserved";

  // font display parameters
  context.font = fontsize.toString() + 'px Segoe UI';
  context.textAlign = 'left'; 
  context.textBaseline = 'bottom'
  
  // attrib. block width for 1 line attribution
  var metrics = context.measureText(attribution);
  var block_width = metrics.width + 2*margin;

  // expand block if necessary
  var canvas_size = getCanvasSize(data.divName); 
  block_width = Math.min(block_width,canvas_size.width)
  
  // wrap text to rectangle width
  var attribution_lines = wrapText(context,attribution,canvas_size.width-2*margin);
  
  // attrib. block height
  var block_height = 2*margin + fontsize + (attribution_lines.length-1)*lineheight;    

  // left & top of full attrib. block
  var pos = getLeftTop(data.divName,data.location,block_width,block_height);

  // background rectangle
  context.globalAlpha=0.5;
  context.fillStyle = '#000';
  context.fillRect(pos.left,pos.top,block_width,block_height);
  
  // display all text lines
  context.globalAlpha=1.0;       
  context.fillStyle = '#FFF';
  
  xtmp = pos.left+margin;
  ytmp = pos.top+margin+fontsize;
  for (var k = 0; k < attribution_lines.length; k++) {
    context.fillText(attribution_lines[k],xtmp,ytmp)
    ytmp += lineheight;
  }
  
  //cleanup
  context.globalAlpha=1.0;
}


function largeAttribution(context,data) {

  // sizing parameters
  var fontsize = 10; //pixels
  var lineheight = 2+fontsize;
  var margin = 5;
  var block_width = 300;
  var img_height = 20;

  // copyright & distribution statement text
  var copytext = 'Imagery \u00A92016 Planet \u00B7 All rights reserved'
  var disttext = 'DISTRIBUTION STATEMENT C: Distribution authorized to U.S. Government Agencies and their contractors (Administrative or Operational Use). Other requests for this document shall be referred to the AFRL, Wright-Patterson Air Force Base, OH 45433-7321.';

  // font display parameters
  context.font = fontsize.toString() + 'px Segoe UI';
  context.textAlign = 'left'; 
  context.textBaseline = 'bottom'
  
  // reduce attrib. block width if necessary
  var canvas_size = getCanvasSize(data.divName);    
  block_width = Math.min(block_width,canvas_size.width);
  
  // scaled image width (accomodate missing/not yet loaded image)
  var img_width;
  if (data.image.width==0) {
    img_height = 0;
    img_width = 0;        
  } else {        
    img_width = img_height * (data.image.width/data.image.height);
  }

  // copyright lines
  // if wrapping is required, eliminate the icon
  var metrics = context.measureText(copytext);
  
  var copylines;
  if (metrics.width <= block_width-3*margin-img_width) {
    copylines = [copytext];        
  } else {
    img_width = 0;
    img_height = 0;
    copylines = wrapText(context,copytext,block_width);
  }   
  
  // expand block width if necessary
  //block_width = Math.max(block_width,4*margin+img_width+copy_width)

  // wrapped distribution statement    
  var distlines = wrapText(context, disttext, block_width-2*margin);

  // block height
  var copylines_height = fontsize + (copylines.length-1)*lineheight;
  var copy_height = Math.max(img_height,copylines_height);
  var dist_height = fontsize + (distlines.length-1)*lineheight;
  var block_height = 3*margin+copy_height+dist_height;
  
  // left & top of full attribution block
  var pos = getLeftTop(data.divName,data.location,block_width,block_height);
  
  
  // draw rectangle
  context.globalAlpha=0.5;
  context.fillStyle = '#000';
  context.fillRect(pos.left,pos.top,block_width,block_height);
  
  // initialize text drawing variables
  var xtmp,ytmp;
  
  // draw image
  if (img_width>0) {
    context.globalAlpha=1;        
    xtmp = pos.left + margin;
    ytmp = pos.top + margin + (copy_height-img_height)/2;
    context.drawImage(data.image,xtmp,ytmp, img_width, img_height); 
  }
  
  // draw copyright text
  context.globalAlpha=1;       
  context.fillStyle = '#FFF';
  
  if (img_width==0) { 
    xtmp = pos.left+margin;
  } else {
    xtmp = pos.left+img_width+2*margin;        
  }
  ytmp = pos.top + margin + (copy_height-copylines_height)/2 + fontsize;
  
  for (var k = 0; k < copylines.length; k++) {
    context.fillText(copylines[k],xtmp,ytmp)
    ytmp += lineheight;
  }
  
  // draw distribution statement text    
  context.globalAlpha=1;       
  context.fillStyle = '#FFF';
  
  xtmp = pos.left+margin;
  ytmp = pos.top+2*margin+copy_height+fontsize;
  for (var k = 0; k < distlines.length; k++) {
    context.fillText(distlines[k],xtmp,ytmp)
    ytmp += lineheight;
  }
  
  // cleanup
  context.globalAlpha=1;
  
}

function wrapText(context, text, maxWidth) {
  var words = text.split(' ');
  var lines = [];    
  
  var line = '';
  for(var n = 0; n < words.length; n++) {
    var testLine = line + words[n] + ' ';
    var metrics = context.measureText(testLine);
    var testWidth = metrics.width;
    if (testWidth > maxWidth && n > 0) {
      lines.push(line);
      line = words[n] + ' ';
    }
    else {
      line = testLine;
    }
  }
  lines.push(line);
  return lines;
}

function getCanvasSize(divName) {
  var width = $("#" + divName).width();
  var height = $("#" + divName).height();
  return {'width': width,'height':height}; 
}

function getLeftTop(divName,location,obj_width,obj_height) {
  var canvas_size = getCanvasSize(divName);

  var left,top;
  switch (location) {
    case 'topleft':
    left = 0;
    top = 0;
    break;
    case 'topright':
    left = canvas_size.width - obj_width;
    top = 0;
    break;
    case 'bottomleft':
    left = 0;
    top = canvas_size.height - obj_height;
    break;
    default:       
    left = canvas_size.width - obj_width;
    top = canvas_size.height - obj_height;
  }
  
  return {'left':left,'top':top};    
}