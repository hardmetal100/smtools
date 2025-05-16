#!/usr/bin/python

import os
import sys
import re

def program(aArgs):
    obj = re.match('[a-z]+ln\d{4}',os.uname()[1])
    if obj!=None:
        aArgs['noCondition']=True
    do_not_dispatch = False
    if aArgs['noCondition']==False:
        f = open("/etc/redhat-release","r")
        lines = f.readlines()
        match = re.match(".*release (\d\.?\d*).*", lines[0])
        val = match.group(1)
        val = float(val)
        if val<5:
            aArgs['allMachines'] = False
            do_not_dispatch = False
        else:
            do_not_dispatch = True
    ## Command building
    options = []
    queue = "batch"
    cmd = "bsub -Is "
    # Select Queue
    if aArgs['interactive']==True:
        cmd += "-q interactive "
    elif aArgs['test']==True:
        cmd += "-q test "
    # Options
    if aArgs['newest']==True:
        options.append("osrel==70")
    # elif aArgs['allMachines']==False and aArgs['test']==False:
    #     options.append("osrel!=40")
    if aArgs['minmem'] is not None:
        options.append("rusage[mem=%d]"%(aArgs['minmem']))
    if aArgs['osrel'] is not None:
        options.append("osrel==%d"%(aArgs['osrel']))
    options = ["-R '%s'"%(o) for o in options]
    cmd += ' '.join(options) + ' '

    if aArgs['ghost']==True:
        cmd += "tcsh -c \'"
    cmd += ' '.join(aArgs['COMMAND'])
    if aArgs['ghost']==True:
        cmd += "\'"

    if do_not_dispatch==True:
        if aArgs['v']==True:
            print ' '.join(aArgs['COMMAND'])
        os.system(' '.join(aArgs['COMMAND']))
    else:
        if aArgs['v']==True:
            print cmd
        os.system(cmd)

if __name__ == '__main__':
    if sys.version_info < (2, 7):
        raise "You must use python 2.7 or greater!"
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interactive', action='store_true', default=False, help="Dispatch interactively")
    parser.add_argument('-g', '--ghost', action='store_true', default=False, help="Dispatch withtout crediting the bsub queue")
    parser.add_argument('-t', '--test', action='store_true', default=False, help="Dispatch to current test queue (mostly the latest server images")
    parser.add_argument('-a', '--allMachines', action='store_true', default=False, help="Dispatch to all machines except RH4")
    parser.add_argument('-n', '--newest', action='store_true', default=False, help="Dispatch to the newest machines only")
    parser.add_argument('-f', '--noCondition', action='store_true', default=False, help="Dispatches even if you are already on the right machine")
    parser.add_argument('-v', action='store_true', default=False, help="Print verbose info")
    parser.add_argument('--minmem',  action='store', default=None, type=int, help="Minimum amount of memory required (in MB)")
    parser.add_argument('--osrel',  action='store', default=None, type=int, help="OS Release version to select")
    parser.add_argument('COMMAND', action='store', default="", nargs='+', help="Command to be executed")
    if len(sys.argv)<2:
        parser.print_help()
    presult = parser.parse_args()
    presult = vars(presult)
    if presult['v']==True:
        print presult
    program(presult)





