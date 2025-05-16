__author__ = 'root'

import sys
import re
import os
import subprocess
import argparse

class ArgumentParser:
    def __init__(self):
        None


class InputFile:
    def __init__(self, path):
        self.path = path
        self.duration = {'hour': 0, 'min': 0, 's': 0, 'ms': 0}
        self.streams = list()
        self.valid = True
        self.characterize()
        return

    def print(self):
        print('InputFile: {path}'.format(path = self.path))
        print('Duration:  {duration}'.format(duration = self.duration))
        print('Streams:   {streams}'.format(streams = self.streams))
        print('Valid:     {valid}'.format(valid = self.valid))
        return

    def addDuration(self, string):
        # Duration: 01:42:00.26, start: 0.000000, bitrate: N/A
        result = re.search('Duration:\s+(?P<hour>\d{2}):(?P<min>\d{2}):(?P<s>\d{2}).(?P<ms>\d{2})', string)
        if result != None:
            for k in self.duration:
                self.duration[k] = result.group(k)
            return True
        else:
            return False

    def addStream(self, string):
        stream = dict()
        # Example 1
        #    Stream #0.0[0x13f7]: Video: h264 (High), yuv420p, 1280x720 [PAR 1:1 DAR 16:9], 50 fps, 90k tbn, 100 tbc
        #    Stream #0.1[0x13f8](deu): Audio: mp2, 48000 Hz, 2 channels, s16p, 192 kb/s
        #    Stream #0.2[0x13f9](fra): Audio: mp2, 48000 Hz, 2 channels, s16p, 192 kb/s
        #    Stream #0.3[0x13fd](mis): Audio: mp2, 48000 Hz, 2 channels, s16p, 192 kb/s
        #    Stream #0.4[0x13fc](mul): Audio: ac3, 48000 Hz, 5.1, fltp, 448 kb/s
        #    Stream #0.5[0x13fb](deu): Subtitle: dvbsub (hearing impaired)
        #    Stream #0.6[0x13fe](fra): Subtitle: dvbsub
        #    Stream #0.7[0x13ff](deu): Subtitle: dvbsub
        # Example 2
        #    Stream #0.0: Video: h264 (High), yuv420p, 1280x720 [PAR 1:1 DAR 16:9], 30k fps, 1k tbn, 180k tbc
        #    Stream #0.1(deu): Audio: vorbis, 48000 Hz, stereo, fltp
        #    Stream #0.2(fra): Audio: vorbis, 48000 Hz, stereo, fltp
        #    Stream #0.3(mis): Audio: vorbis, 48000 Hz, stereo, fltp
        #    Stream #0.4(mul): Audio: vorbis, 48000 Hz, 5.1, fltp
        result = re.search(r'\bStream\s+#(?P<fid>\d)\.(?P<sid>\d+)(?P<hash>\[(0x[0-9a-fA-F]+)\])?(?P<lang>\(\w+\))?:\s+(?P<type>\w+):\s+(?P<properties>.+)', string)
        if result==None:
            return False
        else:
            for i in ['fid', 'sid', 'hash', 'lang', 'type', 'properties']:
                stream[i] = result.group(i)
            self.streams.append(stream)
            return True

    def characterize(self):
        cmd = "avprobe " + self.path
        cmd = cmd.split()
        ffmpeg_result = ""
        try: ffmpeg_result = subprocess.check_output(cmd, stdin = None, stderr = subprocess.STDOUT, shell = False, universal_newlines = False)
        except subprocess.CalledProcessError as e:
            ffmpeg_result = e.output
            self.valid = False
        ffmpeg_result = ffmpeg_result.decode(sys.getdefaultencoding())
        for l in ffmpeg_result.split('\n'):
            self.addDuration(l)
            self.addStream(l)

class Video:
    def __init__(self, path):
        self.name = os.path.splitext(os.path.basename(path))[0]
        self.extensions = [ ".mpg", ".mkv", ".ts" ]
        if os.path.isfile(path):
            self.files = [InputFile(path)]
        else:
            self.files = list()
            for root, dirs, files in os.walk(path, topdown=True, onerror=None, followlinks=False):
                files.sort()
                for f in files:
                    if os.path.splitext(f)[1] in self.extensions:
                        new = InputFile(os.path.join(root,f))
                        if new.valid: self.files.append(new)
        return

    def print(self):
        print('Video: {name}'.format(name = self.name))
        for f in self.files:
            f.print()

def buildDB(args):
    extensions = [ ".mpg", ".mkv", ".ts" ]
    srcdirs = args['srcdir']
    doall   = args['all']
    DB = dict()
    for d in srcdirs:
        key = os.path.basename(d)
        DB[key] = list()
        ## Only files with extension '.mpg' are
        for root, dirs, files in os.walk(d, topdown=True, onerror=None, followlinks=False):
            files.sort()
            for f in files:
                print("file: %s".format(f))
                if os.path.splitext(f)[1] in extensions:
                    new = InputFile(os.path.join(root,f))
                    DB[key].append(new)
    '''for dirs in DB.values():
        for item in dirs:
            print (item.path+":")
            for s in item.streams:
                print "  id: "+s['id']+" type: "+s['type']+" codec: "+s['codec']
    '''
    return DB

def program(args):
    DB = buildDB(args)
    dstdir  = args['dstdir']
    nothing = args['n']
    ensub   = args['subtitle']
    validformats = [ "Audio", "Video" ]
    exit    = False
    generatedFiles = []
    if ensub==True:
        validformats.append("Subtitle")

    for f, inputs in DB.items():
        if os.path.exists(os.path.join(dstdir,f)):
            continue
        ccfiles = 'concat:'
        cmd  = list()
        cmd.append('avconv')
        cmd.append('-i')
        for i,input in enumerate(inputs):
            if i!=0:
                ccfiles += r'|'
            ccfiles += input.path
        cmd.append(ccfiles)
        cmd += '-c:v libx264'.split()
        cmd += '-c:a libvorbis'.split()
        cmd += '-c:s ssc'.split()
        cmd += '-c:d copy'.split()
        cmd += '-map 0'.split(' ')
        for input in inputs:
            for s in input.streams:
                if s['type'] not in validformats:
                    cmd += ('-map -'+s['id'].replace('.',':')).split()
            break ##  break due to concatenation of input files!
        cmd.append(os.path.join(dstdir,f)+'.mkv')
        if nothing==True:
            print (' '.join(cmd))
        else:
            try:
                avconv_result = subprocess.check_output(cmd, stdin=None, stderr=None, shell=False, universal_newlines=True)
                generatedFiles.append(os.path.join(dstdir,f))
            except subprocess.CalledProcessError as e:
                avconv_result = e.output
            if exit:
                print ("Generated files: ")
                print (generatedFiles)
                sys.exit(0)
    print ("Generated files: ")
    print (generatedFiles)
    sys.exit(0)


def convert(args):
    print ("CONVERT")
    #print (args)
    generatedFiles = list()
    validformats = [ "Audio", "Video" ]
    if args.subtitle:
        validformats.append('Subtitle')
    for i in args.i:
        v = Video(i)
        #v.print()
        files = [i.path for i in v.files]
        cmd  = list()
        cmd.append('avconv')
        cmd.append('-i')
        if len(files) > 1:
            cmd.append('concat:' + r'|'.join(files))
        else:
            cmd += files
        if args.format == 'ogg':
            cmd += '-c:v theora'.split()
        else:
            cmd += '-c:v libx264'.split()
        cmd += '-c:a libvorbis'.split()
        cmd += '-c:s xsub'.split()
        cmd += '-c:d copy'.split()
        cmd += '-map 0'.split(' ')
        for input in v.files:
            for s in input.streams:
                if s['type'] not in validformats:
                    cmd += ('-map -' + s['fid'] + ':' + s['sid']).split()
            break ##  break due to concatenation of input files!
        cmd.append(os.path.join(args.o, v.name) + '.mkv')
        if args.n == True:
            print (' '.join(cmd))
        else:
            try:
                avconv_result = subprocess.check_output(cmd, stdin=None, stderr=None, shell=False, universal_newlines=True)
                generatedFiles.append(os.path.join(args.o, v.name) + '.mkv')
            except subprocess.CalledProcessError as e:
                print(e.output)
                sys.exit(-1)
    print("Generated files: ")
    print(generatedFiles)
    sys.exit(0)

def cut(args):
    print ("CUT")
    #print (args)
    generatedFiles = list()
    for i in args.i:
        v = Video(i)
        #v.print()
        files = [i.path for i in v.files]
        cmd  = list()
        cmd.append('avconv')
        cmd.append('-i')
        if len(files) > 1:
            cmd.append('concat:' + r'|'.join(files))
        else:
            cmd += files
        if args.format == 'ogg':
            cmd += '-c:v theora'.split()
        else:
            cmd += '-c:v libx264'.split()
        cmd += '-c:a copy'.split()
        cmd += '-c:s copy'.split()
        cmd += '-c:d copy'.split()
        cmd += '-map 0'.split(' ')
        for input in v.files:
            for s in input.streams:
                if s['type'] not in validformats:
                    cmd += ('-map -' + s['fid'] + ':' + s['sid']).split()
            break ##  break due to concatenation of input files!
        cmd.append(os.path.join(args.o, v.name) + '.mkv')
        if args.n == True:
            print (' '.join(cmd))
        else:
            try:
                avconv_result = subprocess.check_output(cmd, stdin=None, stderr=None, shell=False, universal_newlines=True)
                generatedFiles.append(os.path.join(args.o, v.name) + '.mkv')
            except subprocess.CalledProcessError as e:
                print(e.output)
                sys.exit(-1)
    print("Generated files: ")
    print(generatedFiles)
    sys.exit(0)


if __name__=="__main__":
    ## Main parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help')

    ## Sub Parser: Convert
    parserConvert = subparsers.add_parser('convert', help='Converts a video (shrinks it)')
    parserConvert.add_argument('-i', action='store', nargs='+', required=True, default=None, help="Paths containing the video source (file or directory). If a directory is given, all sub-video files are considered to belong to one video and are concatenated.")
    parserConvert.add_argument('-o', action='store', default=None, required=True, help="Path where the converted videos are stored (directory)")
    parserConvert.add_argument('--subtitle', action='store_true', default=False, help="Includes subtitles")
    parserConvert.add_argument('--format', action='store', default='mkv', help="Select the format, e.g.: mkv, mp4, ogg, ...")
    parserConvert.add_argument('-n', action='store_true', default=False, help="Does not execute but only display what it will do")
    parserConvert.set_defaults(func=convert)

    ## Sub Parser: Cut
    parserCut = subparsers.add_parser('cut', help='Cuts a video (Cut beginning and end)')
    parserCut.add_argument('-i', action='store', nargs='+', required=True, default=None, help="Paths containing the video source (file or directory)")
    parserCut.add_argument('-o', action='store', default=None, required=True, help="Path where the converted videos are stored (directory)")
    parserCut.add_argument('-s', action='store', default=None, required=True, help="Starting time in the format hh:mm:ss")
    parserCut.add_argument('-e', action='store', default=None, required=False, help="End time in the format hh:mm:ss")
    parserCut.add_argument('-n', action='store_true', default=False, help="Does not execute but only display what it will do")
    parserConvert.set_defaults(func=convert)

    ## Parse or display help
    if len(sys.argv)<2:
        parser.print_help()
    else:
        presult = parser.parse_args()
        #presult = vars(presult)
        print (presult)
        presult.func(presult)
        #program(presult)
