###Overview
Calibrates aerial camera models and constructs 3D models from video sequences as well applications for 3D models such as change detection. 

### Cloning

Due to using a privet git-lfs server, cloning the repo is less than trivial

1. Install git lfs (https://git-lfs.github.com/) which requires git 1.8.2 or newer
2. `git lfs init`
1. `mkdir voxel_globe`
2. `cd voxel_globe`
3. `git init .`
4. `git remote add upstream https://github.com/ngageoint/voxel-globe.git`
5. `git fetch`
6. `git config lfs.url {private_lfs_repo}`
7. Install custom cert if needed for lfs server (typically with `update-ca-trust`)
8. Enable git password caching (easiest is `git config --global credential.helper cache`)
9. `git lfs pull` until no errors
8. `git checkout master`
9. `git submodule init`
10. `git submodule update`
11. ./install.bat

###Pull Requests

If you'd like to contribute to this project, please make a pull request. We'll review the pull request and discuss the changes. All pull request contributions to this project will be released under the MIT license.

Software source code previously released under an open source license and then modified by NGA staff is considered a "joint work" (see 17 USC § 101); it is partially copyrighted, partially public domain, and as a whole is protected by the copyrights of the non-government authors and must be released according to the terms of the original open source license.
