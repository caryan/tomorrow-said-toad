---
title: No init system on Ubuntu 18.04 base
date: 2020-02-10
tags:
  - embedded
  - software
summary: Restoring an init system to an Ubuntu 18.04 minimal image
draft: false
---

I had some trouble setting up a Zynq system with [Ubuntu 18.04 base image](http://cdimage.ubuntu.com/ubuntu-base/releases/18.04.3/release/) as the rootfs. The kernel would panic when it handed off to the `rootfs`:
```
5.755108] VFS: Mounted root (ext4 filesystem) on device 179:2.
[    5.764260] devtmpfs: mounted
[    5.767397] Freeing unused kernel memory: 832K
[    5.785642] Run /sbin/init as init process
[    5.801110] Run /etc/init as init process
[    5.805797] Run /bin/init as init process
[    5.810504] Run /bin/sh as init process
[    5.833609] [drm] Cannot find any crtc or sizes
/bin/sh: 0: Can't open earlyprintk
[    5.869633] Kernel panic - not syncing: Attempted to kill init! exitcode=0x00007f00
```

The console messages were on the mark and indeed none of `/sbin/init`, `/etc/init`, `/bin/init` existed and `/bin/sh` links to `dash` which isn't an `init` system. I was a little mystified as to what changed from 16.04 but finally I discovered a [blog post](http://blog.dustinkirkland.com/2018/02/rfc-ubuntu-1804-lts-minimal-images.html) that went over all the additional parts stripped out for the Ubuntu 18.04 minimal image and in particular because containers are king: "This base filesystem tarball also lacks a kernel and an init system, as it's intended to be used inside of a chroot or application container." 

Fortunately, after `chroot` into the `rootfs` a simple `apt-get -y install systemd` will setup `/sbin/init` to link `/sbin/init -> /lib/systemd/systemd` as it should be for an Ubuntu system. 

As a side note I found [Gentoo Linux Chroot](https://wiki.gentoo.org/wiki/Chroot) had the right `mount` incantation for getting `apt-get` in `chroot` to behaving nicely.
```
$ sudo mount --rbind /dev /mnt/mychroot/dev
$ sudo mount --make-rslave /mnt/mychroot/dev
$ sudo mount -t proc /proc /mnt/mychroot/proc
$ sudo mount --rbind /sys /mnt/mychroot/sys
$ sudo mount --make-rslave /mnt/mychroot/sys
$ sudo mount --rbind /tmp /mnt/mychroot/tmp
```
