#!/bin/bash
echo "### START ###"

echo "### Add external users (NAS) ###"
adduser --no-create-home --uid 1024 --ingroup users --disabled-password --disabled-login nasadmin
adduser --no-create-home --uid 1026 --ingroup users stefan
adduser --no-create-home --uid 1027 --ingroup users --disabled-password --disabled-login steffi
adduser --no-create-home --ingroup users ladmin

adduser stefan adm
adduser stefan cdrom
adduser stefan sudo
adduser stefan dip
adduser stefan plugdev 
adduser stefan lpadmin
adduser stefan sambashare

adduser ladmin adm
adduser ladmin cdrom
adduser ladmin sudo
adduser ladmin dip
adduser ladmin plugdev 
adduser ladmin lpadmin
adduser ladmin sambashare

credfile="/home/stefan/.smbcredentials"
fstabfile="/etc/fstab"
nasdir="/mnt/NAS"

#echo "### Home (/dev/sda3) ###"
#echo "# home" >> $fstabfile
#echo "UUID=6718deab-d656-4e7e-b068-e33bc5a69697 /home           #ext4    errors=remount-ro 0       1" >> $fstabfile
#mv /home /home.old
#mount -a

echo "### NFS ###"
echo "Create credentials file $credfile ... "
echo "username=stefan"   >  $credfile
echo "password=Avpx1234" >> $credfile
echo "done"

dirs=()
dirs+=("TV")
dirs+=("Music")
dirs+=("Pictures")
dirs+=("Porn")
dirs+=("Backup")
dirs+=("homes/stefan")
dirs+=("homes/nasroot")
dirs+=("Share")
dirs+=("Programme")
dirs+=("Spiele")
dirs+=("pxe")
dirsUSB=()
dirsUSB+=("Serien")

echo "" >> $fstabfile
echo "" >> $fstabfile


## NFS/SAMBA
apt-get -fy install cifs-utils
apt-get -fy install nfs-common

echo "## NFS mounts" >> $fstabfile

for d in ${dirs[@]};
do
	echo -n "Create directory \"$nasdir/$d\" ... "
	mkdir -p $nasdir/$d
	echo "done"
	echo -n "Create entry for \"$nasdir/$d\" in \"$fstabfile\" ... "
	#echo "//192.168.1.101/$d		$nasdir/$d		cifs  credentials=$credfile,uid=stefan,gid=stefan,nounix,file_mode=0774,dir_mode=0775     0       0" >> $fstabfile
	echo "192.168.1.101:/volume1/$d		$nasdir/$d		nfs	defaults     0       0" >> $fstabfile
	echo "done"
done

echo "## SAMBA mounts" >> $fstabfile

for d in ${dirsUSB[@]};
do
	echo -n "Create directory \"$nasdir/$d\" ... "
	mkdir -p $nasdir/$d
	echo "done"
	echo -n "Create entry for \"$nasdir/$d\" in \"$fstabfile\" ... "
	echo "//192.168.1.101/$d		$nasdir/$d		cifs  credentials=$credfile,uid=stefan,gid=users,nounix,file_mode=0774,dir_mode=0775     0       0" >> $fstabfile
	#echo "192.168.1.101:/volumeUSB/usbshare/$d		$nasdir/$d		nfs	defaults     0       0" >> $fstabfile
	echo "done"
done

mount -a
	
echo "### Install programs ... ###"


## add repositories
apt-add-repository -y ppa:ubuntu-wine/ppa
apt-add-repository -y ppa:me-davidsansome/clementine
apt-get update

## Wine
apt-get -fy install wine
## Clementine
apt-get -fy install clementine
## VIM
apt-get -fy install vim
## Adobe Flash Plugin
apt-get -fy install flashplugin-installer 
## GParted
apt-get -fy install gparted 
## gstreamer libs
apt-get -fy install 'gstreamer*' 
## Remmina
apt-get -fy install remmina
## SSH Server
apt-get -fy install openssh-server 
ssh-keygen -f "/home/stefan/.ssh/known_hosts" -R localhost
## MONO (Silverlight)
apt-get -fy install mono-complete
apt-get -fy install
apt-get -fy install mono-complete
## VLC
apt-get -fy install vlc browser-plugin-vlc
## MP3 / Music tools
apt-get -fy install mp3check
apt-get -fy install fdupes
apt-get -fy install fslint
## avconv (video converting)
apt-get -fy install libav-tools
apt-get -fy install libavcodec-extra-53
apt-get -fy install libavutil-extra-51
## OpenShot
apt-get -fy install openshot
## Audio Converter SoX library
apt-get -fy install libsox-fmt-all 
## Network Performance Test
apt-get -fy install iperf
## Main Menue for GNOME
apt-get -fy install alacarte
apt-get -fy install --no-install-recommends gnome-panel
## Asunder - CD Ripper
apt-get -fy install asunder
## MP3 check/repair
apt-get -fy install mp3diags mp3diags-doc


echo "### INFO ###"
echo "# --> For remote desktop take the integrated 'remmina' clien"
echo "# --> For file synchronization take 'FreeFileSync'"
echo "### FINISHED ###"

