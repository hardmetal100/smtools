#!/bin/bash
## https://wiki.debian.org/VDR
## http://wiki.ubuntuusers.de/VDR
## http://kodi.wiki/view/PVR/Backend/VDR
## 
## Directories:
##  /var/lib/vdr/*
##  /etc/default/vdr
##  /etc/vdr/*
##  /etc/init.d/vdr
##

# Goto temporary directory +copy
mkdir -p /tmp/setup_vdr
cp vdr_remote.conf /tmp/setup_vdr
cd /tmp/setup_vdr
apt-get install -fy libssl-dev
apt-get install -fy git
apt-get install -fy autoconf
apt-get install -fy libtool
apt-get install -fy dvb-apps
apt-get install -fy w-scan
apt-get install -fy linux-firmware-nonfree
git clone https://github.com/OpenELEC/dvb-firmware # has: 24117 firmware!
#lspci -nnk | grep -i VGA -A2 # GET VIDEO HARDWARE
apt-get install i965-va-driver vainfo  # INTEL
#apt-get install fglrx-updates-core fglrx-updates xvba-va-driver vainfo # AMD

# VDR
apt-get install -fy vdr
apt-get install -fy vdr-dev
apt-get install -fy dh-make
vim /etc/default/vdr
## EDIT: OPTIONS="-w 60 -v /storage/tv/video"
mv /var/lib/vdr/remote.conf /var/lib/vdr/remote.conf.orig
cp vdr_remote.conf /var/lib/vdr/remote.conf

## Channel scan:
scan -o vdr /usr/share/dvb/dvb-t/at-All > /var/lib/vdr/channels.conf
# not working (use w_scan) ==> scan -a 1 -p -x 0 -t 1 -o vdr /usr/share/dvb/dvb-s/Astra-19.2E > ~/channels.Astra-19.2E.tv.conf
w_scan -fs -s S19E2 -o 21

## Channel editor:
#wget http://cle4vdr.vdr-developer.org/files/cle4vdr.0.5.3-qt_amd64.tar.gz
#tar xkf cle4vdr.0.5.3-qt_amd64.tar.gz
wget http://cle4vdr.vdr-developer.org/files/cle4vdr.0.5.3-gtk2_amd64.tar.gz
tar xkf cle4vdr.0.5.3-gtk2_amd64.tar.gz


# VDR: Other plugins
#wget http://wirbel.htpc-forum.de/wirbelscan/vdr-wirbelscan-0.0.7.tgz
#tar xkf vdr-wirbelscan-0.0.7.tgz
#pushd wirbelscan-0.0.7
# VDR Manager
git clone http://projects.vdr-developer.org/git/vdr-manager.git


# XBMC
# apt-add-repository -y ppa:team-xbmc/ppa
# apt-add-repository -y ppa:team-xbmc/unstable
apt-add-repository -y ppa:team-xbmc/xbmc-nightly
apt-get update
## <14
apt-get install -fy xbmc
## >14
apt-get install -fy kodi

# VDR:  XVDR Plugin
git clone https://github.com/pipelka/vdr-plugin-xvdr
pushd vdr-plugin-xvdr
make
make install
popd

# XBMC: XVDR Plugin
git clone https://github.com/pipelka/xbmc-addon-xvdr
pushd xbmc-addon-xvdr
# libtoolize --force
# aclocal
# autoheader
# automake --force-missing --add-missing
# autoconf
sh autogen.sh
./configure --prefix=/usr/lib/xbmc
make
make install
popd

## Senderlogos:
mkdir -p /home/vdr/tv/senderlogos
pushd /home/vdr/tv
git clone https://github.com/3PO/Senderlogos senderlogos
popd
## andere logos: http://www.kodinerds.net/index.php/Thread/27408-RELEASE-Deutsche-Senderlogos-optimiert-f%C3%BCr-den-Xperience1080-Skin/?pageNo=1

## service vdr start
## vdr-sfxe

## VDR Startup Script (init.d):
##startvdr()
##{
##    if [ "$ENABLED" != "0" ] ; then
##        # only start vdr if there is no other instance running
##        if start-stop-daemon --start --startas $DAEMON --test \
##            --name $(basename $DAEMON) --pidfile $PIDFILE >/dev/null
##        then
##            ## BEGIN: ADDED BY MIEDLSTE
##            while ! [ -e /dev/dvb/adapter2/frontend0 ]; do
##              sleep 1s;
##            done
##            ## END: ADDED BY MIEDLSTE

# DISABLE UBUNTU SYSTEM CRASH INFO
vim /etc/default/apport # ==> enabled=0

# DISABLE UBUNTU UPDATE NOTIFIER
gconftool -s –type bool /apps/update-notifier/auto_launch false
vim /etc/xdg/autostart/update-notifier.desktop # ==> NoDisplay=false
# ==> disable Startup Application update notifier



#  xbmc-pvr-mythtv-cmyth xbmc-pvr-vuplus xbmc-pvr-vdr-vnsi xbmc-pvr-njoy xbmc-pvr-nextpvr xbmc-pvr-mediaportal-tvserver
#  xbmc-pvr-tvheadend-hts xbmc-pvr-dvbviewer xbmc-pvr-argustv
#  xbmc-pvr-iptvsimple xbmc-audioencoder-vorbis xbmc-audioencoder-flac xbmc-audioencoder-lame

# Bei Problemen mit dem Treiber,koennte moeglicherweise ein loeschen des Verzeichnisses /lib/modules/$(uname -r)/kernel/drivers/media helfen.
# Problemquelle: dmesg: saa716x_tbs_dvb: Unknown symbol stv090x_attach (err -22)
