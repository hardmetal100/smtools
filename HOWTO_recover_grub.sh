#!/bin/bash

mount /dev/sda1 /mnt

mount -o bind /dev /mnt/dev 
mount -o bind /sys /mnt/sys 
mount -t proc /proc /mnt/proc 
#cp /proc/mounts /mnt/etc/mtab 
chroot /mnt /bin/bash

