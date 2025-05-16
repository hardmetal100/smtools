#!/bin/bash

echo Number: $#
if [ $# -ne 1 ]; then
  echo "NO FILENAME GIVEN!!!"
else
  if [ ! -e "$1.ts" ]; then
    echo "FILE $1.ts DOES NOT EXIT"
  else
    export cmd="avconv -i \"$1.ts\" -vcodec libxvid -b 2000k -acodec libmp3lame -ac 2 -ar 44100 -ab 128k \"$1.avi\""
    echo $cmd > exec.cmd
    . ./exec.cmd
  fi
fi 
