#!/usr/sbin/python3

import argparse
import sys

try:
  import P4
except:
  print ("""
  ERROR at 'import P4', module not found!
  Please try to load a python module including the p4python!
  e.g.: module load python/3.6.2 (SWDIG module: /home/swdig/tools/python/3.6.2)
  """)
  sys.exit(1)

def findImport(path):
  p4 = P4.P4()
  p4.connect()
  streams = [s['Stream'] for s in p4.run("streams") if s['Type'] not in ['virtual']]
  #streams = ['//socvoice/refs.codecxs2']
  result = []
  for s in streams:
    #print ('Search in stream "' + s + '"')
    search = [s for s in p4.run('stream', '-o', s)[0]['Paths'] if s.startswith('import')]
    #print (search)
    #print (path)
    for p in search:
      #print (s)
      if path in p:
        #print ('***FOUND***')
        result.append(s)
        break
  p4.disconnect()
  return result


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('paths', nargs='+', help='Stream paths which shall be searched for in import statements')
  if len(sys.argv) < 2:
    parser.print_help()
  args = parser.parse_args()
  for p in args.paths:
    print (findImport(p))


