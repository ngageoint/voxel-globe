function MapViewer() {
}

/**
 * This method is intended to support set up of common map actions so all maps
 * in the UI will have the same behavior for common buttons, clicks, etc.
 */
MapViewer.prototype.setupMap = function(config) { 
  var that = this;
  var shouldRender = true;
  if (config.noRender) {
    shouldRender = false;
  }
  Cesium.BingMapsApi.defaultKey = "0zblO6y6G6YudavPx5Ec~J6IvJKffmtUaoUu71RtArQ~AkhMuWWBuZSBX3HMW_mzrsRa1kzdlXAjxvyzuXlcwb3lhbREm3QuK4m1ZxHw8JhU"

  var shouldGeocode = false;
  if (config.geocoder) {
    shouldGeocode = true;
  }

  // set up the map widget
  this.cesiummap = new Cesium.Viewer('mapWidget', {
    // imageryProvider : new Cesium.ArcGisMapServerImageryProvider({
    //   url : 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer'
    // }),
    useDefaultRenderLoop: shouldRender,
    fullscreenButton: false,
    animation: false,
    baseLayerPicker: true,
    geocoder: shouldGeocode,
    homeButton: true,
    sceneModePicker: false,
    selectionIndicator: false,
    timeline: false,
    navigationHelpButton: false,
    navigationInstructionsInitiallyVisible: false,
    creditContainer: document.createElement('div')  // Hides the credits.
  });

  // Keep a local ref to the main map for use in event-handler closures.
  var mainMap = this.cesiummap;

  // Define some constants to make things a bit easier to read.
  var PI = Cesium.Math.PI;
  var HALF_PI = Cesium.Math.PI_OVER_TWO
  var CURSOR_WIDTH = 2;
  var CURSOR_MATERIAL = Cesium.Color.WHITE;
  var VIEW_MATERIAL = Cesium.Color.YELLOW

  // Set up the overview map widget. The overview map, a.k.a., thumbnail map,
  // a.k.a. mini map, is a secondary map revealed as a little rectangular, 2D,
  // world map, usually positioned in the bottom-right corner of the primary
  // map. It shows the world centered on the approximate current location on
  // the main map.

  // To hold the overview map, two nested divs are added under the main map
  // and styled appropriately for the desired display.
  function styleOverview(div) {
    var INSET = 15;
    var HEIGHT = 150;
    div.css('position', 'absolute')
    div.css('right',  INSET.toString() + 'px'); // Inset overview map from the
    div.css('bottom', INSET.toString() + 'px'); // bottom-right of main map.
    div.css('width',  (HEIGHT * 1.6).toFixed(0).toString() + 'px');
    div.css('height', HEIGHT.toString() + 'px');
    div.css('border', '2px solid white');
    div.css('border-radius', '2px');
  }

  $('.cesium-viewer-bottom').append('<div id="overviewMap" />')
  styleOverview($('#overviewMap'));

  function styleOverviewContainer(div) {
    div.css('width',  '100%')
    div.css('height', '100%')
  }

  $('#overviewMap').append('<div id="overviewMapContainer" />');
  styleOverviewContainer($('#overviewMapContainer'));

  // Create the overview's viewer and turn off, just about everything, that
  // shows inside the overview map.
  var overviewMap = new Cesium.Viewer('overviewMapContainer', {
    animation: false,
    baseLayerPicker: false,
    fullscreenButton: false,
    geocoder: false,
    homeButton: false,
    infoBox: false,
    sceneModePicker: false,
    selectionIndicator: false,
    timeline: false,
    navigationHelpButton: false,
    navigationInstructionsInitiallyVisible: false,
    orderIndependentTranslucency: false,
    creditContainer: document.createElement('div'),  // Hides the credits.
    sceneMode: Cesium.SceneMode.SCENE2D,
    mapProjection: new Cesium.WebMercatorProjection()
  });

  // Set overview map properties to disable direct manipulation.
  function conditionOverviewScene(scene) {
    scene.screenSpaceCameraController.enableLook      = false;
    scene.screenSpaceCameraController.enableRotate    = false;
    scene.screenSpaceCameraController.enableTilt      = false;
    scene.screenSpaceCameraController.enableTranslate = false;
    scene.screenSpaceCameraController.enableZoom      = false;
  }

  conditionOverviewScene(overviewMap.scene);

  // Rather than trying to construct the imagery, from scratch, it seems
  // safer to grab what's already been added to the main map. Later in this
  // file, there is an event listener that will continue to do this, as new
  // layers are added to the main map.
  function addImageryFromMainMap(mainMap) {
    for (i = 0; i < mainMap.imageryLayers.length; i++) {
      overviewMap.imageryLayers.addImageryProvider(
        mainMap.imageryLayers.get(i).imageryProvider);
    }
  }

  addImageryFromMainMap(mainMap);

  // The following methods add drawing entities to the overview map in
  // response to where the main map's camera is positioned.

  // Given a camera position, in radians and as probably fetched from the main
  // map, draw a vertical cursor to represent the position of the camera. This
  // cursor should appear as a straight vertical line in the middle of the
  // overview map.
  function addVerticalCursor(lng, lat) {
    overviewMap.entities.add({
      name: "verticalCursor",
      polyline: {
        positions: Cesium.Cartesian3.fromRadiansArray([
          0.0, -HALF_PI,  // South pole.
          lng, lat,       // Mid-point -- where map is centered.
          0.0, HALF_PI    // North pole.
        ]),
        width: CURSOR_WIDTH,
        material: CURSOR_MATERIAL
      }
    });
  }

  // Given a camera position, in radians and as probably fetched from the main
  // map, draw a horizontal cursor to represent the position of the camera. As
  // this cursor is a a line of constant latitude on a Mercator projection, it
  // will actually render as a curve -- unless the camera position happens
  // to be on the equator.
  //
  // Note, as the "off to the west/east" longitudes get closer to the edge of
  // the overview map's display area, things can get a little wonky with
  // Cesium -- sometimes with odd behaviors -- like all drawing entities will
  // disappear. The most reliable work-around, I've found, is to inset the
  // longitudes, slightly, from the edge of the display limits. After some
  // experimentation, 1/100th pi seems to be reliable. DAL - 19-Oct-2016.
  function addHorizontalCursor(lng, lat) {
    var LNG_EXTENT = (PI - (PI / 100.0));  // How much to the left and right.
    overviewMap.entities.add({
      name: "horizontalCursor",
      polyline: {
        positions: Cesium.Cartesian3.fromRadiansArray([
          lng - LNG_EXTENT, -lat,   // Off to the west.
          lng,               lat,   // Mid-point -- where map is centered.
          lng + LNG_EXTENT, -lat    // Off to the east.
        ]),
        width: CURSOR_WIDTH,
        material: CURSOR_MATERIAL
      }
    });
  }

  // Given a rectangle representing the view of the main map, draw a bounding
  // box on the overview map.
  //
  // Note: There is a documented feature, in Cesium, to close a bounding poly-
  // line. For whatever reason, I've hit a bug, that folks seem to have
  // encountered, the causes the entire entity to just not render -- no error
  // message and the entity is added to the Cesium viewer, but won't show.
  // Go figure. Anyway, the easy work around is to just add a final point that
  // is the same as the first. This has proven reliable. DAL - 17-Oct-2016
  function addViewExtent(r) {
    overviewMap.entities.add({
      name: "viewExtent",
      polyline: {
        positions: Cesium.Cartesian3.fromRadiansArray([
          r.west, r.north,
          r.west, r.south,
          r.east, r.south,
          r.east, r.north,
          r.west, r.north
        ]),
        width: CURSOR_WIDTH,
        material: VIEW_MATERIAL
      }
    });
  }

  // Adjust the overview map's position, right or left, based on the current
  // position of the main map's camera. This method is also used from inside
  // the camera-move event handler.
  function scrollOverview(mainMap) {
    var lng = mainMap.scene.camera.positionCartographic.longitude;
    var lat = mainMap.scene.camera.positionCartographic.latitude;
    // Since this is a Mercator projection, the extreme top and bottom of
    // the view are very distorted. Distorted to the point of being rather
    // distracting to the user. Cesium provides guidance about limiting the
    // view to avoid the extreme latitudes; however, in practice, this
    // wasn't enough. So, the amount reported by Cesium is tripled and that
    // seems to provide a reasonable behavior.
    var vert_extent = 3.0 *
      (HALF_PI - Cesium.WebMercatorProjection.MaximumLatitude);
    overviewMap.camera.setView({
      destination: new Cesium.Rectangle(lng - PI, -vert_extent,
                                        lng + PI,  vert_extent)
    });
    addVerticalCursor(lng, lat);
    addHorizontalCursor(lng, lat)
  }

  scrollOverview(mainMap);   // Render initial view of the overview map!

  // Based on how the camera has moved in the main map, update the overview
  // map by adjusting the map's position -- remove any existing drawing
  // entities, scroll the map into position, and redraw the cursors. If
  // the view in the main map has all four corners well defined on the globe,
  // draw a rectangle representing the extent of the main map's view.
  function onCameraMoved(mainMap) {
    overviewMap.entities.removeAll();
    scrollOverview(mainMap);
    var view = mainMap.scene.camera.computeViewRectangle();
    if (!(view === undefined) && view.width < PI && view.height < PI) {
      addViewExtent(view);
    }
  }

  // Appends an imagery layer so we can see something that looks like
  // a map. This may be too clever; but, imagery is added to the overview
  // by hooking the main map's "layerAdded" event. This should keep the
  // display in the overview map looking just like contents of the main map.
  function onLayerAdded(layer) {
    overviewMap.imageryLayers.addImageryProvider(layer.imageryProvider);
  }

  // Register event listeners for changes in the main map.

  mainMap.scene.imageryLayers.layerAdded.addEventListener(onLayerAdded);

  mainMap.scene.camera.moveEnd.addEventListener(function () {
    onCameraMoved(mainMap);
  });

  // use STK terrain by default
  if (config.useSTKTerrain) {
    // pretty sure this code does not work
    var terrainProvider = new Cesium.CesiumTerrainProvider({
       url : '//assets.agi.com/stk-terrain/world'
    });
    this.cesiummap.terrainProvider = terrainProvider;
    // but this does! Use STK terrain by simulating click on that button.
    $(".cesium-baseLayerPicker-item")[16].click();
  }

  // disable the cesium buttons as jquery buttons, otherwise they look bad
  $(function() {
    if ($(".cesium-button").button('instance')) {
      $(".cesium-button").button('destroy');
    }
  })

/*
  var ellipsoid = Cesium.Ellipsoid.WGS84;
  var south = Cesium.Math.toRadians(this.centerLat - this.zoomLevel)
  var west = Cesium.Math.toRadians(this.centerLon - this.zoomLevel);
  var north = Cesium.Math.toRadians(this.centerLat + this.zoomLevel);
  var east = Cesium.Math.toRadians(this.centerLon + this.zoomLevel);

  var extent = new Cesium.Rectangle(west, south, east, north);
  this.cesiummap.scene.camera.viewRectangle(extent, ellipsoid); */
  // TODO : Use this to restore original view someday
  // this.originalTilt = this.cesiummap.scene.camera.tilt;
  // this.originalHeading = this.cesiummap.scene.camera.heading;
  // this originalDirection = this.
  // var direction = this.cesiummap.scene.camera.direction;
  // this.originalDirection = new Cesium.Cartesian3(direction.x, direction.y, direction.z);
  
  this.cesiummap.homeButton.viewModel.command.beforeExecute
      .addEventListener(function (commandInfo) {
    //Zoom to custom extent
    var camera = that.cesiummap.scene.camera;
    console.log("Returning camera to center position.");
    
    that.cesiummap.scene.camera.lookAtTransform(Cesium.Matrix4.IDENTITY);
    // changed 9/10/15, that.cesiummap.scene.camera.setTransform(Cesium.Matrix4.IDENTITY);

    /*console.log("Camera direction: " + camera.direction);
    console.log("Camera position: " + camera.position);
    console.log("Camera tilt: " + camera.tilt);
    
    camera.tilt = that.originalTilt;
    camera.heading = that.originalHeading;
    camera.direction.x = that.originalDirection.x;
    camera.direction.y = that.originalDirection.y;
    camera.direction.z = that.originalDirection.z;
    */
   
    that.viewHomeLocation();

    //Tell the home button not to do anything.
    commandInfo.cancel = true;
  });

  // set a cookie recording the current camera position
  var that = this;
  this.cesiummap.clock.onTick.addEventListener(function() {
    var cam = that.cesiummap.camera;
    var pos = cam.position;
    var dir = cam.direction;
    var up = cam.upWC;
    setCameraCookie("cameraPosition", JSON.stringify(pos), 30);
    setCameraCookie("cameraDirection", JSON.stringify(dir), 30);
    setCameraCookie("cameraUp", JSON.stringify(up), 30);
  });

  document.addEventListener('keydown', function(e) {
    if (e.keyCode == 82 && document.activeElement == document.body) {
      that.topDown();
    }
  });

  var viewer = this.cesiummap;
  var handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
  handler.setInputAction(function(movement) {
    cameraHeight = viewer.camera.positionCartographic.height;
    viewer.camera.zoomIn(cameraHeight / 2);
  }, Cesium.ScreenSpaceEventType.LEFT_DOUBLE_CLICK);
}

MapViewer.prototype.getCesiumViewer = function() {
  return this.cesiummap;
}

MapViewer.prototype.topDown = function() {
  var viewer = this.cesiummap;
  var windowPosition = new Cesium.Cartesian2(viewer.container.clientWidth / 2, 
    viewer.container.clientHeight / 2);
  var pickRay = viewer.scene.camera.getPickRay(windowPosition);
  var centerPosition = viewer.scene.globe.pick(pickRay, viewer.scene);

  if (centerPosition) {
    var camPos = viewer.scene.camera.position;
    var camPosCartographic = viewer.scene.globe.ellipsoid
        .cartesianToCartographic(camPos);
    var height = camPosCartographic.height;
    viewer.camera.lookAt(centerPosition,
      new Cesium.HeadingPitchRange(0, -Cesium.Math.PI, height));
    viewer.camera.lookAtTransform(Cesium.Matrix4.IDENTITY);
  } else {
    viewer.camera.setView({
      heading : -Cesium.Math.PI,
      pitch : 0
    })
  }
}

MapViewer.prototype.viewHomeLocation = function() {
  var that = this;
  if (this.homeEntity != null) {
    this.cesiummap.zoomTo(this.homeEntity);
  } else if (this.extent != null) {
    this.cesiummap.camera.setView({  // setView -> flyTo for animation
      destination : that.extent
    });
  } else if (this.center != null) {
    this.cesiummap.camera.setView({  // setView -> flyTo for animation
      destination : that.center
/*        orientation: {
        heading : 0.0,
        pitch : -Cesium.Math.PI_OVER_TWO,
        roll : 0.0
      } */
    });
  } else if (getCameraCookie("cameraPosition") !== "" &&
             getCameraCookie("cameraDirection") !== "" &&
             getCameraCookie("cameraUp") !== "") {
    var pos = JSON.parse(getCameraCookie("cameraPosition"));
    var dir = JSON.parse(getCameraCookie("cameraDirection"));
    var up = JSON.parse(getCameraCookie("cameraUp"));
    this.cesiummap.camera.setView({
      destination: pos,
      orientation: {
        direction: dir,
        up: up
      }
    })
  } else {
    console.log("No home location has been defined for the map...");
  }
}

MapViewer.prototype.setBoundingRectangle = function(west, south, east, north) {
//var ellipsoid = Cesium.Ellipsoid.WGS84;
  var extent = Cesium.Rectangle.fromDegrees(west, south, east, north);
  this.extent = extent;
  console.log("Set the extent to " + south + ", " + west + " and " + north + ", " + east);
//  this.cesiummap.scene.camera.viewRectangle(this.extent, ellipsoid); 
  this.viewHomeLocation();
}

MapViewer.prototype.setHomeLocation = function(centerLat, centerLon, centerAlt) {
  this.centerLat = centerLat;
  this.centerLon = centerLon;
  this.centerAlt = centerAlt;

  this.center = Cesium.Cartesian3.fromDegrees(this.centerLon, 
    this.centerLat,
    this.centerAlt
  );
  /*this.zoomLevel = 0.07;
  var ellipsoid = Cesium.Ellipsoid.WGS84;
  var south = Cesium.Math.toRadians(this.centerLat - this.zoomLevel)
  var west = Cesium.Math.toRadians(this.centerLon - this.zoomLevel);
  var north = Cesium.Math.toRadians(this.centerLat + this.zoomLevel);
  var east = Cesium.Math.toRadians(this.centerLon + this.zoomLevel);

  this.extent = new Cesium.Rectangle(west, south, east, north);*/
  this.viewHomeLocation();
}

// If the map has a home entity defined, calling viewHomeLocation() will focus
// it on that entity (so you don't have to calculate the camera's location or
// bounding rectangle by hand, since cesium's zoomTo(entity) method does this
// automatically).
MapViewer.prototype.setHomeEntity = function(entity) {
  console.log("Set the home entity to " + entity.name);
  this.homeEntity = entity;
  //this.viewHomeLocation();
}

function setCameraCookie(cname, cvalue, exdays) {
  var expires;
  if (exdays) {
      var date = new Date();
      date.setTime(date.getTime() + (exdays * 24 * 60 * 60 * 1000));
      expires = "; expires=" + date.toGMTString();
  }
  else {
      expires = "";
  }
  var re = /\/(\w+)\/?$/;
  var app = window.location.pathname.match(re)[1]
  cname = cname + '_' + app;
  cvalue = cvalue.replaceAll("\"", "\'")
  document.cookie = cname + "=" + cvalue + "; " + expires + "; path=/;";
}

function getCameraCookie(cname) {
  var re = /\/(\w+)\/?$/;
  var app = window.location.pathname.match(re)[1]
  cname = cname + '_' + app;
  var name = cname + "=";
  var ca = document.cookie.split(';');
  for(var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0)==' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      var ret = c.substring(name.length,c.length);
      ret = ret.replaceAll("\'", "\"");
      return ret;
    }
  }
  return "";
}

String.prototype.replaceAll = function(search, replace) {
    if (replace === undefined) {
      return this.toString();
    }
    return this.replace(new RegExp('[' + search + ']', 'g'), replace);
};
