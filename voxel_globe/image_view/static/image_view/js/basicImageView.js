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
  var gsd = 20;
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
  
    // one-time load of attribution image
    //attributionMode = 'old'; // 'old'|'large'|'small'
    var attributionMode = 'large';
    var attributionImg = loadAttribution(attributionMode);
    
    // Affix attribution to bottom right of canvas
    vectorLayer.on('precompose', function(event) {
      var ctx = event.context;
      ctx.save();
      var canvas_width = $("#" + that.divName).width();
      var canvas_height = $("#" + that.divName).height();
      // var img = new Image();
      // img.src = "/static/image_view/icons/banner.png";
      // var img_width = img.width;
      // var img_height = img.height;
      // //alert(that.divName)
      // var x = canvas_width - img_width;
      // var y = canvas_height - img_height;
      // ctx.globalAlpha = 0.8;
      // ctx.drawImage(img, x, y);
      // ctx.globalAlpha = 1; 
      displayAttribution(ctx,attributionImg,canvas_width,canvas_height,attributionMode);
    });

    vectorLayer.on('postcompose', function(event) {
      var ctx = event.context;
      ctx.restore();
    })

    var clipAnimationInterval = 30;
    var clipSize = 0;
    // Restrict the visible window of the image when zoomed to a high res
    littleImageLayer.on('precompose', function(event) {
      var goalClipSize = getClipSize();
      if (goalClipSize < clipSize) {
        clipSize -= Math.min(clipAnimationInterval, clipSize - goalClipSize);
      } else if (goalClipSize > clipSize) {
        clipSize += Math.min(clipAnimationInterval, goalClipSize - clipSize);
      }
      // var clipSize = getClipSize();
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
      event.frameState.animate = true;
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




function loadAttribution(mode) {
    
    var img = new Image();
    img.onload = function() {
        console.log('ATTRIBUTION IMAGE LOADED');
    }
    
    switch (mode) {
        case "old":
            img.src = "/static/image_view/icons/banner.png";
            break;
        default:
            img.src = "/static/image_view/icons/planet.svg";
    }
    return img    
}
         

function displayAttribution(context,img,right,bottom,mode) {    
    switch (mode) {
        case 'large':
            largeAttribution(context,img,right,bottom);
            break;
        case 'small':
            smallAttribution(context,img,right,bottom);
            break;
        default:
            oldAttribution(context,img,right,bottom);
    }    
}

function oldAttribution(context,img,right,bottom) {
    
    var img_width = img.width;
    var img_height = img.height;
    
    var x = right - img_width;
    var y = bottom - img_height;
    
    context.globalAlpha = 0.8;
    context.drawImage(img, x, y, img_width, img_height);
    context.globalAlpha = 1;    
}

function smallAttribution(context,img,right,bottom) {
    var fontsize = 12; //pixels
    var margin = 5;
    var attribution = "Distribution Statement C \u00B7 Imagery \u00A92016 Planet \u00B7 All rights reserved";
    
    context.font = fontsize.toString() + 'px Segoe UI';
    context.textAlign = 'left'; 
    context.textBaseline = 'middle'
    
    var boxheight = fontsize + 2*margin;
    
    var metrics = context.measureText(attribution);
    var boxwidth = metrics.width + 2*margin;
        
    var left = right-boxwidth;
    var top = bottom-boxheight; 
                 
    context.globalAlpha=0.5;
    context.fillStyle = '#000';
    context.fillRect(left,top,boxwidth,boxheight);
    
    context.globalAlpha=1.0;       
    context.fillStyle = '#FFF';
    context.fillText(attribution,left+margin,top+(boxheight/2))
    
    context.globalAlpha=1.0;
}


function largeAttribution(context,img,right,bottom) {
    var fontsize = 10; //pixels
    var lineheight = 2+fontsize;
    var margin = 5;
    var boxwidth = 400;
    var imgheight = 20;

    context.font = fontsize.toString() + 'px Segoe UI';
    context.textAlign = 'left'; 
    
    // scaled image size
    if (img.width==0) {
        imgheight = 0;
        var imgwidth = 0;        
    } else {        
        var imgwidth = imgheight * (img.width/img.height);
    }

    // copyright text    
    var copytext = 'Imagery \u00A92016 Planet \u00B7 All rights reserved'
    var metrics = context.measureText(copytext);
    var copywidth = metrics.width;    
    
    // expand box width if necessary
    boxwidth = Math.max(boxwidth,4*margin+imgwidth+copywidth)
           
    // wrapped distribution statement
    var tmp = 'DISTRIBUTION STATEMENT C: Distribution authorized to U.S. Government Agencies and their contractors (Administrative or Operational Use). Other requests for this document shall be referred to the AFRL, Wright-Patterson Air Force Base, OH 45433-7321.';
    var disttext = wrapText(context, tmp, boxwidth-2*margin);
    
    // box height
    var copyheight = Math.max(imgheight,fontsize);
    var distheight = fontsize + (disttext.length-1)*lineheight;
    var boxheight = 3*margin+copyheight+distheight;
    
    // upper right corner
    var x = right-boxwidth;
    var y = bottom-boxheight;    
    
    // inialize temp. variables
    var xtmp = 0;
    var ytmp = 0;
    
    // draw box
    context.globalAlpha=0.5;
    context.fillStyle = '#000';
    context.fillRect(x,y,boxwidth,boxheight);
    
    // draw image
    context.globalAlpha=1;
    context.drawImage(img, x+margin, y+margin, imgwidth, imgheight); 
    
    // draw copyright text
    if (imgwidth==0) { 
        xtmp = x+margin;
    } else {
        xtmp = x+imgwidth+3*margin;        
    }
    ytmp = y+margin+(copyheight/2)-.05*imgheight;
    
    context.globalAlpha=1;       
    context.fillStyle = '#FFF';
    context.textBaseline = 'middle'
    context.fillText(copytext,xtmp,ytmp);
    
    // draw distribution statement text    
    context.globalAlpha=1;       
    context.fillStyle = '#FFF';
    context.textBaseline = 'alphabetic'
    
    xtmp = x+margin;
    ytmp = y+2*margin+copyheight+fontsize;
    for (var k = 0; k < disttext.length; k++) {
        context.fillText(disttext[k],xtmp,ytmp)
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
