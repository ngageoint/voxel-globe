/* 
 * Models a Handle billboard (the eight black corners and up/down arrows on the 
 * bounding cube). Given the lat, lon, and height, adds a billboard
 * with the correct icon to that position on the cesium globe, and 
 * adds the billboard to the given Cesium.BillboardCollection. Listens for click
 * and drag events, upon which it updates its own position, the positions of
 * the other associated corners and the bounding box as a whole, and the numbers
 * in the form data.
 */

function Handle(long, lat, height, collection, name, mapViewer) {
  var viewer = mapViewer.getCesiumViewer();
  var scene = viewer.scene;
  var prev = {
    values: {},
    position: new Cesium.Cartesian3()
  }

  var p = new Cesium.Cartesian3.fromRadians(long, lat, height);
  if (name == "top" || name == "bottom") {
    var img = iconFolderUrl + name + ".png";
  } else {
    var img = iconFolderUrl + "corner.png";
  }

  if (name == "bottom") {
    var eye = getEyeOffset(p);
  } else {
    var eye = new Cesium.Cartesian3(0,0,-10);
  }

  var me = collection.add({
    position: p,
    image : img,
    eyeOffset : eye,
    id : [this, name]
  });

  function getEyeOffset(this_position) {
    var camera_position = scene.camera.position;
    var dist = Cesium.Cartesian3.distance(camera_position, this_position);
    var z = (0 - Math.abs(dist)) + 10;
    return new Cesium.Cartesian3(0, 0, z);
  }

  if (name == "bottom") {
    var oldCamPos = scene.camera.position.clone();
    var oldMePos = me.position.clone();

    mapViewer.getCesiumViewer().clock.onTick.addEventListener(function() {
      var newCamPos = scene.camera.position.clone();
      var newMePos = me.position.clone();
      // update eye offset in case camera position has changed
      // update based on own pos as well, in case moved by other corners
      if (!newCamPos.equals(oldCamPos) || !newMePos.equals(oldMePos)) {
        me.eyeOffset = getEyeOffset(newMePos);
        oldCamPos = newCamPos;
        oldMePos = newMePos;
      }
    })
  }

  // click and drag listeners inspired by leforthomas's cesium-drawhelper,
  // https://github.com/leforthomas/cesium-drawhelper

  this.onClick = function(position) {
    enableRotation(false);

    // store the current values and position in prev object for error recovery
    prev.values = $.extend({}, mapViewer.values);
    prev.position = Cesium.Cartesian3.clone(me.position);
    var plane = findIntersectingPlane();

    function onDrag(position) {
      var pickRay = scene.camera.getPickRay(position);
      // find the intersection of the plane and the pickRay; this is the new pos
      me.position = Cesium.IntersectionTests.rayPlane(pickRay, plane);

      mapViewer.drawUpdateBoundingBox(me.position, name);
      updateFormFields(mapViewer.values);
      mapViewer.updateCorners();
    }

    function onDragEnd() {
      handler.destroy();
      enableRotation(true);
      var v = mapViewer.validateBoundingBox(mapViewer.values, true);
      // console.log(v);
      // true here means that it should adjust the values if invalid
      // e.g., if north < south, instead of returning an error, switch the two
      if (v !== "valid") {
        if (typeof v === "string") {
          // if an error string is returned, alert the user, then
          // recover from the error by restoring the previous values
          alert(v);
          mapViewer.values = prev.values;
          me.position = prev.position;
          mapViewer.drawUpdateBoundingBox(me.position, name);
          updateFormFields(mapViewer.values);
          mapViewer.updateCorners();
        } else {
          // if a values object is returned, it means we had to switch values
          // e.g. north became south, so replace the old values, update the form
          // fields, and redraw the box based on the new values
          mapViewer.values = v;
          updateFormFields(mapViewer.values);
          mapViewer.updateAllEdges(mapViewer.values);
        }
      }
    }

    function findIntersectingPlane() {
      // When using the mouse position, it's necessary to first find the plane
      // that passes through this point and is parallel to the tangent plane on
      // the ellipsoid surface. Then find the intersection of this plane with the
      // pickRay defined by that position, so it doesn't always consider the
      // picked position to be on the surface of the globe.

      if (name == "top" || name == "bottom") {
        // find the plane using three coplanar points
        var a = me.position;
        var b = collection.get(0).position;  // southwest top
        var c = collection.get(2).position;  // southwest bottom
        var v0 = subtract(a, b);  // subtract a from b and store in v0
        var v1 = subtract(c, b);  // subtract b from c and store in v1
        var normal = cross(b, a);  // compute cross-product of v0 and v1
        var plane = Cesium.Plane.fromPointNormal(a, normal, plane);
        return plane;
      } else {
        // based on a coplanar point and the normal vector, find the plane
        var coplanar = me.position;
        var normal = new Cesium.Cartesian3();
        Cesium.Ellipsoid.WGS84.geocentricSurfaceNormal(coplanar, normal);
        var plane = Cesium.Plane.fromPointNormal(coplanar, normal);
        return plane;
      }
    }

    function enableRotation(enable) {
      scene.screenSpaceCameraController.enableRotate = enable;
    }

    function subtract(left, right) {
      var result = new Cesium.Cartesian3();
      result.x = left.x - right.x;
      result.y = left.y - right.y;
      result.z = left.z - right.z;
      return result;
    }

    function cross(left, right) {
      var result = new Cesium.Cartesian3();
      var leftX = left.x;
      var leftY = left.y;
      var leftZ = left.z;
      var rightX = right.x;
      var rightY = right.y;
      var rightZ = right.z;

      var x = leftY * rightZ - leftZ * rightY;
      var y = leftZ * rightX - leftX * rightZ;
      var z = leftX * rightY - leftY * rightX;

      result.x = x;
      result.y = y;
      result.z = z;
      return result;
    }

    var handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);

    handler.setInputAction(function(movement) {
      onDrag(movement.endPosition);
    }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);

    handler.setInputAction(function(movement) {
      onDragEnd(scene.camera.pickEllipsoid(movement.position));
    }, Cesium.ScreenSpaceEventType.LEFT_UP);
  }
}
