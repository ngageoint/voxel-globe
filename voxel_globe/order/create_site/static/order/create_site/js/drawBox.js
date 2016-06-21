function DrawBox() {
  var mapViewer, viewer, handler, tooltip, start, rectangle;
  var clicked = false, dragged = false, drawing = false;
  var pos = {};
  var that = this;

  this.init = function(v) {
    mapViewer = v;
    viewer = v.getCesiumViewer();
    viewer.scene.globe.depthTestAgainstTerrain = false;

    tooltip = new Tooltip("mapWidget");
    tooltip.text("Drag to navigate, click to create");

    handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);

    // on left down, register that the mouse is down
    handler.setInputAction(
      function(click) {
        clicked = true;
      }, Cesium.ScreenSpaceEventType.LEFT_DOWN
    );

    // on left up, release the mouse and if not already drawing, start drawing
    // if already drawing, this is the second click, so finish drawing
    handler.setInputAction(
      function(click) {
        if (!clicked) {
          return;
        }
        clicked = false;
        if (!dragged) {
          var cartesian = viewer.scene.camera.pickEllipsoid(click.position);
          var cartographic = 
            Cesium.Ellipsoid.WGS84.cartesianToCartographic(cartesian);
          if (!drawing) {
            startDrawing(cartographic);
          } else {
            stopDrawing(cartographic);
          }
        }
      }, Cesium.ScreenSpaceEventType.LEFT_UP
    );

    handler.setInputAction(
      function(movement) {
        var position = viewer.scene.camera.pickEllipsoid(movement.endPosition)
        if (clicked) {
          dragged = true;
        } else {
          if (drawing) {
            var cartographic = 
                Cesium.Ellipsoid.WGS84.cartesianToCartographic(position);
            draw(cartographic);
          }
          dragged = false;
        }
      }, Cesium.ScreenSpaceEventType.MOUSE_MOVE
    );
  }

  function startDrawing(cartographic) {
    drawing = true;
    tooltip.text("Click again to finish drawing");
    start = new Cesium.Cartographic.fromRadians(cartographic.longitude, 
        cartographic.latitude, 0);
    var pos = new Cesium.Cartesian3.fromRadians(cartographic.longitude, 
        cartographic.latitude, 0);
    
    if (mapViewer.corners) {
      mapViewer.corners.removeAll();
    } else {
      mapViewer.corners = new Cesium.BillboardCollection();
    }

    var img = iconFolderUrl + "corner.png";
    var eye = new Cesium.Cartesian3(0, 0, -100);

    var southeast = mapViewer.corners.add({
      position: pos,
      image: img,
      eyeOffset : eye,
      id: 'se'
    });

    var southwest = mapViewer.corners.add({
      position: pos,
      image: img,
      eyeOffset : eye,
      id: 'sw'
    });

    var northeast = mapViewer.corners.add({
      position: pos,
      image: img,
      eyeOffset : eye,
      id: 'ne'
    });

    var northwest = mapViewer.corners.add({
      position: pos,
      image: img,
      eyeOffset : eye,
      id: 'nw'
    });

    viewer.scene.primitives.add(mapViewer.corners);

    pos.s = cartographic.latitude; pos.n = cartographic.latitude;
    pos.e = cartographic.longitude; pos.w = cartographic.longitude;
    updateFormFieldsWrapper(10);

    var coords = new Cesium.Rectangle(start.longitude, start.latitude,
        start.longitude + 0.0000000001, start.latitude + 0.0000000001);
    if (rectangle) {
      viewer.entities.remove(rectangle);
    }

    rectangle = viewer.entities.add({
      rectangle : {
        coordinates : coords,
        outline : true,
        outlineColor : Cesium.Color.WHITE,
        outlineWidth : 3,
        material : Cesium.Color.WHITE.withAlpha(0.4)
      },
      name : "rectangle"
    });
  }

  function draw(cartographic) {
    pos.s = Math.min(cartographic.latitude, start.latitude);
    pos.n = Math.max(cartographic.latitude, start.latitude);
    pos.e = Math.max(cartographic.longitude, start.longitude);
    pos.w = Math.min(cartographic.longitude, start.longitude);
    updateFormFieldsWrapper(cartographicDistance(start, cartographic));
    var scratch = new Cesium.Cartesian3();

    for (var i = 0; i < 4; i++) {
      update(mapViewer.corners.get(i));
    }

    var coords = new Cesium.Rectangle(pos.w, pos.s, pos.e, pos.n);
    rectangle.rectangle.coordinates = coords;

    function update(corner) {
      var lat = pos[corner.id[0]];
      var lon = pos[corner.id[1]];
      corner.position = new Cesium.Cartesian3.fromRadians(lon, lat, 0);
    }

  }

  function stopDrawing(cartographic) {
    drawing = false;
    // send the drawing off to be created by the mapviewer
    var values = updateFormFieldsWrapper(cartographicDistance(start, cartographic));

    // destroy the handler, since we have a box now and are done drawing
    destroy();

    mapViewer.createBoundingBox(values);

    if (!mapViewer.homeEntity) {
      // if the map viewer doesn't have a home entity now, that means there
      // was a user error - so we don't destroy the handlers, we restart the
      // draw process instead
      $('.bbox.degree').val('');
      that.init(mapViewer);
      return;
    }

    viewer.scene.globe.depthTestAgainstTerrain = true;
    mapViewer.boundingBox.description = "The bounding box specified here will " +
      "determine the boundaries of the scene being analyzed. Change any of the " +
      "values in the form or click and drag the image to update the bounding " +
      "box estimates."
    enableClear(true);
    if (allInputsValid()) {
      enableSubmit(true);
    }
  }

  function updateFormFieldsWrapper(distance) {
    var values = {};
    values.north = Cesium.Math.toDegrees(pos.n);
    values.south = Cesium.Math.toDegrees(pos.s);
    values.east = Cesium.Math.toDegrees(pos.e);
    values.west = Cesium.Math.toDegrees(pos.w);
    values.top = Math.abs(distance) / 4;
    values.bottom = 0;
    updateFormFields(values);
    return values;
  }

  function cartographicDistance(p1, p2) {
    var a1 = Cesium.Ellipsoid.WGS84.cartographicToCartesian(p1);
    var a2 = Cesium.Ellipsoid.WGS84.cartographicToCartesian(p2);
    var d = Cesium.Cartesian3.distance(a1, a2);
    return d;
  }

  this.destroy = destroy;

  function destroy() {
    if (!handler.isDestroyed()) {
      handler.destroy();
    }
    if (rectangle) {
      viewer.entities.remove(rectangle);
    }
    if (mapViewer.corners) {
      mapViewer.corners.removeAll();
    }
    tooltip.turnOff();
  }
}
