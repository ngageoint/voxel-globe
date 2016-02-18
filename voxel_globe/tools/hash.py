from hashlib import sha256 as _sha256

def sha256_file(filename, chunk_size=1024*1024*16):
  ''' Helper function for hashing a single file '''

  hasher = _sha256()
  chunk = 1024*1024*16

  with open(filename, 'rb') as fid:
    data = fid.read(chunk)
    while data:
      hasher.update(data)
      data = fid.read(chunk)

  return hasher.hexdigest()
