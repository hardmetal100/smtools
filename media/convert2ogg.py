#!/usr/bin/python

import sys
import re
import os
import argparse
import subprocess

def program(aArgs):
	path       = aArgs['path']
	extensions = aArgs['types']
	nothing    = aArgs['n']
	remove     = aArgs['remove']
	found      = []
	for root, dirs, files in os.walk(path, topdown=True, onerror=None, followlinks=True):
		for f in files:
			for e in extensions:
				#rex = re.compile('([\w -]+).'+e)
				rex = re.compile('(.+)\.'+e)
				result = rex.match(f)
				if result!=None:
					found.append((os.path.join(root,result.group(1)),e))
	for f in found:
		cmd  = 'sox "'
		cmd += f[0] + '.' + f[1]
		cmd += '" -t ogg "'
		cmd += f[0] + '.ogg"'
		delete = 'rm -f "' + f[0] + '.' + f[1] + '"'
		if nothing:
			print cmd
			if remove:
				print delete
		else:
			print "Convert:", os.path.basename(f[0])+'.'+f[1]
			stat = os.system(cmd)
			if remove and stat==0:
				print "Delete file ..."
				os.system(delete)
# 	print "FOUND: "
# 	print found


if __name__=="__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--path', action='store', default=None, help="Root path for the search")
	parser.add_argument('-t', '--types', action='store', nargs='+', default=None, help="File types to be converted (give extension ==> e.g.: mp3, mp2, wav, ...)")
	parser.add_argument('-r', '--remove', action='store_true', default=False, help="Remove original files")
	parser.add_argument('-n', action='store_true', default=False, help="Does not execute but only display what it will do")
	if len(sys.argv)<2:
		parser.print_help()
	presult = parser.parse_args()
	presult = vars(presult)
	#print presult
	program(presult)

