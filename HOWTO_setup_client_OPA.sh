#!/bin/bash
echo "### START ###"

echo "### Add external users (NAS) ###"
adduser --no-create-home --ingroup users hermann

adduser hermann adm
adduser hermann cdrom
adduser hermann sudo
adduser hermann dip
adduser hermann plugdev 
adduser hermann lpadmin
adduser hermann sambashare

## NFS/SAMBA
apt-get -fy install cifs-utils
apt-get -fy install nfs-common
	
echo "### Install programs ... ###"
## TeamViewer
#wget http://www.teamviewer.com/download/teamviewer_linux.deb
#dpkg -i teamviewer_linux.deb
#apt-get -f install
#dpkg -i teamviewer_linux.deb
## JEDIT
#apt-get -fy install jedit
## Wine
apt-add-repository -y ppa:ubuntu-wine/ppa
apt-get update
apt-get -fy install wine
## LibreOffice
#apt-add-repository -y ppa:libreoffice/ppa 
#apt-get update
#apt-get -fy install libreoffice
## VIM
#apt-get -fy install vim
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
ssh-keygen -f "/home/hermann/.ssh/known_hosts" -R localhost
## MONO (Silverlight)
apt-get -fy install mono-complete
apt-get -fy install
apt-get -fy install mono-complete
## VLC
apt-get -fy install vlc browser-plugin-vlc
## Unetbootin
apt-get -fy install unetbootin
## RecordMyDesktop
apt-get -fy install gtk-recordmydesktop
## avconv (video converting)
apt-get -fy install libav-tools
apt-get -fy install libavcodec-extra-53
apt-get -fy install libavutil-extra-51
## Thunderbird
apt-get -fy install thunderbird


echo "### INFO ###"
echo "# --> For remote desktop take the integrated 'remmina' clien"
echo "# --> For file synchronization take 'FreeFileSync'"
echo "### FINISHED ###"

