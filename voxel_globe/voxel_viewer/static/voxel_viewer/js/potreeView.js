
function PotreeViewer() {
}

PotreeViewer.prototype.initialize = function(potreeConfig, mapViewer) {

  this.mapViewer = mapViewer;

  // add EPSG:21781 projection definition
  proj4.defs('EPSG:21781', "+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333 +k_0=1 +x_0=600000 +y_0=200000 +ellps=bessel +towgs84=674.4,15.1,405.3,0,0,0,0 +units=m +no_defs ");

  var swiss = proj4.defs("EPSG:21781");
  var WGS84 = proj4.defs("WGS84");

  // boundaries in EPSG:21781 
  //var minSwiss = [589500, 231300, 722.505];
  //var maxSwiss = [590099, 231565.743, 776.4590];
  var minSwiss = [589500, 231300, 722.505];
  var maxSwiss = [590099, 231565.743, 776.4590];

  // boundaries in WGS84
  this.minWGS84 = proj4(swiss, WGS84, [minSwiss[0], minSwiss[1]]);
  this.maxWGS84 = proj4(swiss, WGS84, [maxSwiss[0], maxSwiss[1]]);

  this.potreeContainer = document.getElementById("potreeWidget");

  this.three = {
    renderer: null,
    camera: null,
    scene: null
  };

  this.potree = {
    pointcloud: null
  };

  // For debugging, set up the map from here to synchronize views
  // create polygon from boundaries in WGS84
  var entity = {
    name : 'Switzerland',
    polygon : {
    hierarchy : Cesium.Cartesian3.fromDegreesArray([
      this.minWGS84[0], this.minWGS84[1],
      this.maxWGS84[0], this.minWGS84[1],
      this.maxWGS84[0], this.maxWGS84[1],
      this.minWGS84[0], this.maxWGS84[1],
      ]),
    material : Cesium.Color.RED.withAlpha(0.2),
    //height: 100,
    outline : true,
    outlineColor : Cesium.Color.BLACK
    }
  };
  var wyoming =  mapViewer.getCesiumViewer().entities.add(entity);
  
  var cartToVec = function(cart){
      return new THREE.Vector3(cart.x, cart.y, cart.z);
  };
    
  // Compute this stuff for inside the potree rendering loop   
  this.bottomLeft    = cartToVec(Cesium.Cartesian3.fromDegrees(this.minWGS84[0], this.minWGS84[1]));
  this.topLeft     = cartToVec(Cesium.Cartesian3.fromDegrees(this.minWGS84[0], this.maxWGS84[1]));
  this.bottomLeftHigh  = cartToVec(Cesium.Cartesian3.fromDegrees(this.minWGS84[0], this.minWGS84[1], 1));

  // use direction from bottom left to top left as up-vector
  this.latDir  = new THREE.Vector3().subVectors(this.topLeft, this.bottomLeft).normalize();

  //mapViewer.setBoundingRectangle(this.minWGS84[0], this.minWGS84[1], this.maxWGS84[0], this.maxWGS84[1]);
  
  mapViewer.setHomeLocation((this.minWGS84[1] + this.maxWGS84[1]) / 2, (this.minWGS84[0] + this.maxWGS84[0]) / 2, 1000);

  // end map synchronization
  
  this.initThree(); // initialize Three JS
}

PotreeViewer.prototype.initThree = function(){

  var fov = 75;
  var width = 1;
  var height = 1;
  var aspect = width / height;
  var near = 1;
  var far = 10*1000*1000;

  this.three.scene = new THREE.Scene();
  this.three.camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
  this.three.renderer = new THREE.WebGLRenderer({alpha: true});
  this.potreeContainer.appendChild(this.three.renderer.domElement);
  
  var sg = new THREE.SphereGeometry(1);
  var sm = new THREE.Mesh(sg, new THREE.MeshNormalMaterial());
  this.three.scene.add(sm);
  
  this.three.camera.position.set(200,200,200);
  this.three.camera.lookAt(new THREE.Vector3(0,0,0));
  
  var that = this;

  Potree.POCLoader.load("/images/vol_total/cloud.js", function(geometry){
  
    var pointcloud = new Potree.PointCloudOctree(geometry);
    pointcloud.material.pointSizeType = Potree.PointSizeType.ADAPTIVE;
    pointcloud.material.size = 1;

    that.three.scene.add(pointcloud);
    
    that.potree.pointcloud = pointcloud;    
  });
}

PotreeViewer.prototype.renderPotree = function(){

  // register threejs scene with cesium 
  if(this.potree.pointcloud){ 
    this.three.camera.fov = Cesium.Math.toDegrees(this.mapViewer.getCesiumViewer().camera.frustum.fov)
    this.three.camera.updateProjectionMatrix();
    
      //potree.pointcloud.showBoundingBox = true;
      
    this.potree.pointcloud.position.copy(this.bottomLeft);
    this.potree.pointcloud.lookAt(this.bottomLeftHigh);
    this.potree.pointcloud.up.copy(this.latDir);
    
    this.three.camera.matrixAutoUpdate = false;
    var cvm = this.mapViewer.getCesiumViewer().camera.viewMatrix;
    var civm = this.mapViewer.getCesiumViewer().camera.inverseViewMatrix;
    this.three.camera.matrixWorld.set(
      civm[0], civm[4], civm[8 ], civm[12], 
      civm[1], civm[5], civm[9 ], civm[13], 
      civm[2], civm[6], civm[10], civm[14], 
      civm[3], civm[7], civm[11], civm[15]
    );
    this.three.camera.matrixWorldInverse.set(
      cvm[0], cvm[4], cvm[8 ], cvm[12], 
      cvm[1], cvm[5], cvm[9 ], cvm[13], 
      cvm[2], cvm[6], cvm[10], cvm[14], 
      cvm[3], cvm[7], cvm[11], cvm[15]
    ); 
    
    this.three.camera.lookAt(new THREE.Vector3(0, 0, 0));
  }

  var width = this.potreeContainer.clientWidth;
  var height = this.potreeContainer.clientHeight;
  var aspect = width / height;
  
  this.three.camera.aspect = aspect;
  this.three.camera.updateProjectionMatrix();

  // Debugging output...
  
  var cameraText = "THREE: " + this.three.camera.zoom + ", " 
      + this.three.camera.position.x + ", "  + this.three.camera.position.y + ", "  + this.three.camera.position.z + ", " 
      + this.three.camera.fov  + ", " + this.three.camera.aspect
      + ", " + this.three.camera.near + ", " + this.three.camera.far + "<br>";

  var mapCamera = this.mapViewer.getCesiumViewer().camera;
  cameraText += "CESIUM: " + mapCamera.position.x + ", " + mapCamera.position.y + ", " + mapCamera.position.z + ", " 
  + mapCamera.frustum.fov + ", " + mapCamera.frustum.near + ", " + mapCamera.frustum.far + "<br>";

  var tilingRectangle = this.mapViewer.getCesiumViewer().terrainProvider.tilingScheme.rectangle;
  cameraText += "width = " + tilingRectangle.width + " height = " + tilingRectangle.height;

  $('#debugInfo').html(cameraText);
  
  this.three.renderer.setSize(width, height);
  
  this.three.renderer.render(this.three.scene, this.three.camera);
}

PotreeViewer.prototype.update = function(){
  if(this.potree.pointcloud){
    this.potree.pointcloud.update(this.three.camera, this.three.renderer);
  } 
}
