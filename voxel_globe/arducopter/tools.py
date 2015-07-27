
class AdjTaggedMetadata(object):
  def __init__(self, line=None):
    if line:
      (self.filename, n) = line.split(' ', 1);
      n = map(float, n.split(' '));
      self.llh_xyz = [n[0], n[1], n[2]];
      #degrees, meters
      self.yrp = n[3:] 
      #degrees
    else:
      raise Exception('Not implemented yet');
  
  def __str__(self):
    return self.filename + (' %0.12g'*3) % (self.llh_xyz[1], self.llh_xyz[0], self.llh_xyz[2])
  
  def __repr__(self):
    return '%s@%s@%s' % (self.filename, self.llh_xyz, self.yrp) 

def loadAdjTaggedMetadata(filename):
  images = []
  with open(filename, 'r') as fid:
    fid.readline();
    for line in fid:
      images += [AdjTaggedMetadata(line)];
      
  return images;