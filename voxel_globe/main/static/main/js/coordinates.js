function llh2grs80(lon, geodetic_lat, el, a, b){
  if (typeof a == "undefined") { a = 6378137; }
  if (typeof b == "undefined") { b = 6356752.3; }
  geocentric_lat = Math.atan((b/a)*(b/a)*Math.tan(geodetic_lat))
  s = Math.sin(geocentric_lat)
  c = Math.cos(geocentric_lat)
  local_radius = (a*b)/Math.sqrt((b*b*c*c+a*a*s*s))
  x = (local_radius*c + el*Math.cos(geodetic_lat))*Math.cos(lon)
  y = (local_radius*c + el*Math.cos(geodetic_lat))*Math.sin(lon)
  z =  local_radius*s + el*Math.sin(geodetic_lat)

  return [x, y, z]
};

function compute_scale(lon, lat, el){
  lat_r = lat*Math.PI/180.
  lon_r = lon*Math.PI/180.
  g1 = llh2grs80(lon_r, lat_r, el)
  //console.log(g1)
  g2 = llh2grs80(lon_r, lat_r+1e-6, el)
  //console.log(g2)
  lat_scale = 1e-6/Math.sqrt((g1[0]-g2[0])*(g1[0]-g2[0]) + (g1[1]-g2[1])*(g1[1]-g2[1]) + (g1[2]-g2[2])*(g1[2]-g2[2]))

  g1 = llh2grs80(lon_r, lat_r, el)
  g2 = llh2grs80(lon_r+1e-6, lat_r, el)
  lon_scale = 1e-6/Math.sqrt((g1[0]-g2[0])*(g1[0]-g2[0]) + (g1[1]-g2[1])*(g1[1]-g2[1]) + (g1[2]-g2[2])*(g1[2]-g2[2]))

  return [lon_scale, lat_scale]
};

function local_to_global(x, y, z, origin_lon, origin_lat, origin_el){
  scale = compute_scale(origin_lon, origin_lat, origin_el)
  //console.log(scale)

  global_lon = x*scale[0]*180/Math.PI + origin_lon
  global_lat = y*scale[1]*180/Math.PI + origin_lat
  global_el = z + origin_el

  return [global_lat, global_lon, global_el]
};

function global_to_local(lon, lat, el, origin_lon, origin_lat, origin_el){
  scale = compute_scale(origin_lon, origin_lat, origin_el)
  x = (lon - origin_lon)*Math.PI/180/scale[0]
  y = (lat - origin_lat)*Math.PI/180/scale[1]
  z = (el - origin_el)

  return [x, y, z]
}
