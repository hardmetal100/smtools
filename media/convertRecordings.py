#!/usr/bin/python

import sys
import re
import os
import argparse
import subprocess


def program(aArgs):
    srcdirs = aArgs['srcdir']
    dstdir  = aArgs['dstdir']
    ensub   = aArgs['subtitle']
    exit    = not aArgs['not_only_one']
    nothing = aArgs['n']
    extensions = ( ".mpg", ".mkv", ".ts" )
    validformats = ( "Audio", "Video" )
    info_cmd   = "ffmpeg -i"
    unmap = list()
    generatedFiles = list()
    
    for d in srcdirs:
        ## Only files with extension '.mpg' are 
        files = [ f for f in os.listdir(d) if f[-4:] in extensions and (os.path.isfile(os.path.join(d,f)) or os.path.islink(os.path.join(d,f))) ]
        for f in files:
            if os.path.exists(os.path.join(dstdir,f)):
                continue
            cmd  = list()
            cmd += info_cmd.split(' ')
            cmd.append(os.path.join(d,f))
            if nothing==True:
                print ' '.join(cmd)
            ffmpeg_result = ""
            try: ffmpeg_result = subprocess.check_output(cmd, stdin=None, stderr=subprocess.STDOUT, shell=False, universal_newlines=False)
            except subprocess.CalledProcessError as e:
                 ffmpeg_result = e.output
            for l in ffmpeg_result.split('\n'): ##\[0x[0-9a-fA-F]+\]: (\w+): 
                result = re.match('\s+Stream #(\d\:\d+)\[0x[0-9a-fA-F]+\]([\(\)\w]*): (\w+): (.+)', l)
                if result!=None and result.group(3) not in validformats:
                    unmap_ = "-map -"+result.group(1)
                    unmap += unmap_.split(' ')
            cmd  = list()
            cmd += 'avconv -i'.split(' ')
            cmd.append(os.path.join(d,f))
            cmd += '-c:v libx264 -c:a libvorbis -sn -c:d copy -map 0'.split(' ')
            cmd += unmap
            cmd.append(os.path.join(dstdir,f))
            if nothing==True:
                print ' '.join(cmd)
            try:
                avconv_result = subprocess.check_output(cmd, stdin=None, stderr=None, shell=False, universal_newlines=False)
                generatedFiles.append(os.path.join(dstdir,f))
            except subprocess.CalledProcessError as e:
                avconv_result = e.output
            if exit:
                print "Generated files: "
                print generatedFiles
                sys.exit(0)
    print "Generated files: "
    print generatedFiles
    sys.exit(0)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--srcdir', action='store', nargs='+', required=True, default=None, help="Paths containing the video source")
    parser.add_argument('--dstdir', action='store', default=None, required=True, help="Paths where the converted videos are stored")
    parser.add_argument('--subtitle', action='store_true', default=False, help="Includes subtitles")
    parser.add_argument('--not-only-one', action='store_true', default=False, help="Processes all files in the srcdirs")
    parser.add_argument('-n', action='store_true', default=False, help="Does not execute but only display what it will do")
    if len(sys.argv)<2:
        parser.print_help()
    else:
        presult = parser.parse_args()
        presult = vars(presult)
        print presult
        program(presult)
