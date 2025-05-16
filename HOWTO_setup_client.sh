#!/bin/bash
echo "### START ###"

echo "### Add external users (NAS) ###"
adduser --no-create-home --uid 1024 --ingroup users --disabled-password --disabled-login nasadmin
adduser --no-create-home --uid 1026 --ingroup users stefan
adduser --no-create-home --uid 1027 --ingroup users --disabled-password --disabled-login steffi

adduser stefan adm
adduser stefan cdrom
adduser stefan sudo
adduser stefan dip
adduser stefan plugdev 
adduser stefan lpadmin
adduser stefan sambashare

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

dirs[0]="TV"
dirs[1]="Music"
dirs[2]="Pictures"
dirs[3]="Porn"
dirs[4]="Backup"
dirs[5]="homes/stefan"
dirs[6]="Share"
dirsUSB[0]="Serien"

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

mound -a
	
echo "### Install programs ... ###"
## TeamViewer
wget http://www.teamviewer.com/download/teamviewer_linux.deb
dpkg -i teamviewer_linux.deb
apt-get -f install
dpkg -i teamviewer_linux.deb
## JEDIT
apt-get -fy install jedit
## PlayOnLinux
wget -q "http://deb.playonlinux.com/public.gpg" -O- | apt-key add -
wget "http://deb.playonlinux.com/playonlinux_$(lsb_release -cs).list" -O /etc/apt/sources.list.d/playonlinux.list
apt-get update
apt-get -fy install playonlinux
apt-get -fy install curl
## Wine
apt-add-repository -y ppa:ubuntu-wine/ppa
apt-get update
apt-get -fy install wine
## Virtual Box
wget -q http://download.virtualbox.org/virtualbox/debian/oracle_vbox.asc -O- | apt-key add -
sh -c 'echo "deb http://download.virtualbox.org/virtualbox/debian saucy non-free contrib" >> /etc/apt/sources.list.d/virtualbox.org.list'
apt-get update
apt-get -fy install virtualbox virtualbox-qt virtualbox-dkms virtualbox-guest-dkms
## Clementine
apt-add-repository -y ppa:me-davidsansome/clementine
apt-get update
apt-get -fy install clementine
## LibreOffice
apt-add-repository -y ppa:libreoffice/ppa 
apt-get update
apt-get -fy install libreoffice
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
## aMule
apt-get -fy install amule
## Unetbootin
apt-get -fy install unetbootin
## RecordMyDesktop
apt-get -fy install gtk-recordmydesktop
## remmina
apt-get -fy install remmina
## FreeFileSync
wget http://downloads.sourceforge.net/project/freefilesync/freefilesync/archive/FreeFileSync_5.22_Ubuntu_13.04_64-bit.tar.gz?r=http%3A%2F%2Fsourceforge.net%2Fprojects%2Ffreefilesync%2F&ts=1390666687&use_mirror=optimate
tar -xvzf FreeFileSync_6.0_Ubuntu_13.10_64-bit.tar.gz
mv FreeFileSync /opt/
pushd /usr/bin/
ln -s /opt/FreeFileSync/FreeFileSync .
popd
## avconv (video converting)
apt-get -fy install libav-tools
apt-get -fy install libavcodec-extra-53
## Audio Converter SoX library
apt-get -fy install libsox-fmt-all 
## Taschenrechner
apt-get -fy install gcalctool 
## Thunderbird
apt-get -fy install thunderbird
## Network Performance Test
apt-get -fy install iperf 


echo "### INFO ###"
echo "# --> For remote desktop take the integrated 'remmina' clien"
echo "# --> For file synchronization take 'FreeFileSync'"
echo "### FINISHED ###"

