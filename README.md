###Overview
Calibrates aerial camera models and constructs 3D models from video sequences as well applications for 3D models such as change detection. 

### Cloning

1. Install and update CentOS 7
2. Install cuda and git-lfs (don't forget to run `git lfs install`!)
3. `GIT_LFS_SKIP_SMUDGE=1 git clone --recursive https://github.com/ngageoint/voxel-globe`
4. `cd {git_repo}`
5. `echo "https://vsiro:VSIreadonly1@vsi-ri.visualstudio.com" > .pw~`
6. `git config credential.helper "store --file .pw~"`
7. `git lfs pull`

### Building

1. `./install.bat`. You need to say yes to everything except the `run setup` 
question at least once. 

The `run setup` question is important for creating users and setting permissions 
when running in deployment mode. It will also set the firewall rules too. If 
you say no to `run setup`, you can individually choose to setup any of these 3 
steps. They change permissions for deployment, and make development difficult.

### Configuring voxel-globe

There are many variables that can be added to `local_vip.env`, but the most common
include

```
export VIP_IMAGE_SERVER_PORT=8443
export VIP_IMAGE_SERVER_HOST=local.myserver.com
export VIP_IMAGE_SERVER_PROTOCOL=https

export VIP_HTTPD_PORT=8080
export VIP_HTTPD_SSL_PORT=8443
export VIP_HTTPD_SERVER_NAME=${VIP_IMAGE_SERVER_HOST}

```

### Starting voxel-globe

1. `./daemon.bat all start`

If during install, `run setup` was selected, then run `./daemon all start` as root

### Stopping voxel-globe

1. `./daemon.bat all stop`

If during install, `run setup` was selected, then run `./daemon all stop` as root

###Pull Requests

If you'd like to contribute to this project, please make a pull request. We'll review the pull request and discuss the changes. All pull request contributions to this project will be released under the MIT license.

Software source code previously released under an open source license and then modified by NGA staff is considered a "joint work" (see 17 USC § 101); it is partially copyrighted, partially public domain, and as a whole is protected by the copyrights of the non-government authors and must be released according to the terms of the original open source license.
