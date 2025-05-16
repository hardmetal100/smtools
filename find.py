#!/usr/bin/python

import sys
import re
import os
import argparse
import subprocess
def program(aArgs):
    path    = aArgs['PATH']
    diropt  = aArgs['dir']
    nothing = aArgs['n']
    found   = []
    for root, dirs, files in os.walk(path, topdown=True, onerror=None, followlinks=True):
        if diropt!=None:
            if 'nofiles' in diropt and len(files)==0:
                found.append(root)
            if 'nodirs' in diropt and len(dirs)==0:
                found.append(root)
    for f in found:
        print f
#     print "FOUND: "
#     print found

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('PATH', action='store', default=None, help="Root path for the search")
    parser.add_argument('--dir', action='store', nargs='+', default=None, choices=['nofiles', 'nodirs'], help="File types to be converted (give extension ==> e.g.: mp3, mp2, wav, ...)")
    parser.add_argument('-n', action='store_true', default=False, help="Does not execute but only display what it will do")
    if len(sys.argv)<2:
        parser.print_help()
    presult = parser.parse_args()
    presult = vars(presult)
    print presult
    program(presult)