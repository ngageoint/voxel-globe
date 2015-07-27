from numpy import sin, cos, pi, arctan, arctan2

def llh2enu_au(llh_origin, llh):
  ''' someone else's code''' 
  a = 6378137.0;
  b = 6356752.3142;
  e2 = 1 - (b/a)**2;
  
  phi = llh_origin[0]*pi/180.0;
  lam = llh_origin[1]*pi/180.0;
  h   = llh_origin[2];
  
  dphi = llh[0]*pi/180.0 - phi;
  dlam = llh[1]*pi/180.0 - lam;
  dh   = llh[2] - h;
  
  tmp1 = (1-e2*sin(phi)**2)**0.5;
  cl = cos(lam);
  sl = sin(lam);
  cp = cos(phi);
  sp = sin(phi);
  
  de = (a/tmp1+h)*cp*dlam - (a*(1-e2)/(tmp1**3)+h)*sp*dphi*dlam +cp*dlam*dh;
  dn = (a*(1-e2)/tmp1**3 + h)*dphi + 1.5*cp*sp*a*e2*dphi**2 + sp**2*dh*dphi + 0.5*sp*cp*(a/tmp1 +h)*dlam**2;
  du = dh - 0.5*(a-1.5*a*e2*cp**2+0.5*a*e2+h)*dphi**2 - 0.5*cp**2*(a/tmp1 -h)*dlam**2;
  
  return [de, dn, du]

def llh2enu(lat_origin, lon_origin, h_origin, lat, lon, h):
  ''' Take a lon lat height (degrees and meters) origin point and lat lon 
      height number or numpy array) and returns the e, n, u, at the origin'''
  xyz = llh2xyz(lat, lon, h);
  enu = xyz2enu(lat_origin, lon_origin, h_origin, *xyz)
  enu_dict = {'east':enu[0], 'north':enu[1], 'up':enu[2]}
  return enu

def enu2llh(lat_origin, lon_origin, h_origin, east, north, up):
  ''' llh origin can be 1x1 each
      enu can be a numpy array each'''
  xyz = enu2xyz(lat_origin, lon_origin, h_origin, east, north, up)
  llh = xyz2llh(*xyz);
  llh_dict = {'lat':llh[0], 'lon':llh[1], 'h':llh[2]}
  return llh_dict;

def llh2xyz(lat,lon,h):
  # Convert lat, long, height in WGS84 to ECEF X,Y,Z
  # lat and long given in decimal degrees.
  # altitude should be given in meters
  lat = lat/180.0*pi; #converting to radians
  lon = lon/180.0*pi; #converting to radians
  a = 6378137.0; # earth semimajor axis in meters
  f = 1/298.257223563; # reciprocal flattening
  e2 = 2*f -f**2; # eccentricity squared

  chi = (1-e2*(sin(lat))**2)**0.5;
  X = (a/chi +h)*cos(lat)*cos(lon);
  Y = (a/chi +h)*cos(lat)*sin(lon);
  Z = (a*(1-e2)/chi + h)*sin(lat);

  return (X, Y, Z);

def xyz2enu(refLat, refLong, refH, X, Y, Z):
  # convert ECEF coordinates to local east, north, up

  # find reference location in ECEF coordinates
  Xr,Yr,Zr = llh2xyz(refLat,refLong, refH);

  refLat = refLat/180.0*pi;
  refLong = refLong/180.0*pi;

  e = -sin(refLong)*(X-Xr) + cos(refLong)*(Y-Yr);
  n = -sin(refLat)*cos(refLong)*(X-Xr) - sin(refLat)*sin(refLong)*(Y-Yr) + cos(refLat)*(Z-Zr);
  u = cos(refLat)*cos(refLong)*(X-Xr) + cos(refLat)*sin(refLong)*(Y-Yr) + sin(refLat)*(Z-Zr);

  return (e, n, u)

def enu2xyz(refLat, refLong, refH, e, n, u):
  # Convert east, north, up coordinates (labeled e, n, u) to ECEF
  # coordinates. The reference point (phi, lambda, h) must be given. All distances are in metres
 
  [Xr,Yr,Zr] = llh2xyz(refLat,refLong, refH); # location of reference point
 
  refLat = refLat/180.0*pi;
  refLong = refLong/180.0*pi;

  X = -sin(refLong)*e - cos(refLong)*sin(refLat)*n + cos(refLong)*cos(refLat)*u + Xr;
  Y = cos(refLong)*e - sin(refLong)*sin(refLat)*n + cos(refLat)*sin(refLong)*u + Yr;
  Z = cos(refLat)*n + sin(refLat)*u + Zr;

  return (X, Y, Z)

def xyz2llh(X,Y,Z):
  ''' go from x, y, z, (nunpy array in meters) and converts to lon, lat, height '''
  a = 6378137.0; # earth semimajor axis in meters
  f = 1/298.257223563; # reciprocal flattening
  b = a*(1-f);# semi-minor axis
 
  e2 = 2*f-f**2;# first eccentricity squared
  ep2 = f*(2-f)/((1-f)**2); # second eccentricity squared
 
  r2 = X**2+Y**2;
  r = (r2)**0.5;
  E2 = a**2 - b**2;
  F = 54*b**2*Z**2;
  G = r2 + (1-e2)*Z**2 - e2*E2;
  c = (e2*e2*F*r2)/(G*G*G);
  s = ( 1 + c + (c*c + 2*c)**0.5 )**(1/3);
  P = F/(3*(s+1/s+1)**2*G*G);
  Q = (1+2*e2*e2*P)**0.5;
  ro = -(e2*P*r)/(1+Q) + ((a*a/2)*(1+1/Q) - ((1-e2)*P*Z**2)/(Q*(1+Q)) - P*r2/2)**0.5;
  tmp = (r - e2*ro)**2;
  U = ( tmp + Z**2 )**0.5;
  V = ( tmp + (1-e2)*Z**2 )**0.5;
  zo = (b**2*Z)/(a*V);

  lat = arctan( (Z + ep2*zo)/r )*180/pi;
  lon = arctan2(Y,X)*180/pi;
  h = U*( 1 - b**2/(a*V));

  return (lat, lon, h)