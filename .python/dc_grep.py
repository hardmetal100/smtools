import sys
import os
import argparse
import re

#try:
#  import networkx as nx
#else:
#  print ("NetworkX not available with this Python version! Please try to locate one with NetworkX installed (python/3.6.2)")

try:
  import ete3
  ete3_loaded = True
except:
  ete3_loaded = False
  print ("ETE3 not available with this Python version! Please try to locate one with ETE3 installed (python/3.6.2)")

class DC_AreaReportParsing:
  def __init__(self):
    self.hierarchy = []
    return

  def __wrap(self, string):
    return "->[" + string + "]"

  def __unwrap(self, string):
    string = string.lstrip("->[")
    string = string.rstrip("]")
    return string

  def hierarchy_update(self, name, level):
    '''
    Updates the hierarchy table with the latest element.
    First all elements lower or equal than the current hierarchy are deleted.
    Then the new element is added.
    :param name: name of the hierarchy element
    :param level: level of the hierarchy element
    :return: None
    '''
    # Update hierarchy
    while len(self.hierarchy) > 0 and level <= self.hierarchy[-1][1]:
      self.hierarchy = self.hierarchy[:-1]
    # Add level
    self.hierarchy.append((name, level))
    return

  def hierarchy_leaf(self, level=0):
    '''
    Returns the current hierarchy leaf or None
    :param level: the leaf level, 0 is real leaf, 1 is one before the leaf
    :return: current hierarchy leaf name or None
    '''
    if len(self.hierarchy) > level:
      return self.hierarchy[-1 - level][0]
    else:
      return None
  def parse(self, file, check):
    # Check available modules
    if not ete3_loaded:
      print ("DC_AreaReportParsing requires ETE3!")
      sys.exit(1)
    # Read file
    fcontent = f.readlines()
    # Skip header
    while fcontent[0].strip()[:len("Reference Name")] != "Reference Name":
      fcontent = fcontent[1:]
    # Process header
    header = re.split(r'\s{2,}', fcontent[0].strip())
    #print (header)
    fcontent = fcontent[2:]
    ###dictionary = dict()
    ###nxg = nx.DiGraph()
    tree = ete3.Tree(format=1)
    for line in fcontent:
      # Extract indent
      indent = re.match(r'(\s*)', line)
      indent = len(indent.group(1))
      # Extract line columns
      line = re.split(r'\s{2,}', line.strip())
      # Check filter
      skip = True
      if len(line) == len(header):
        for k,v in check.items():
          if k in header:
            # Identify type
            try:
              x = int(line[header.index(k)])
              etype = int
            except:
              try:
                x = float(line[header.index(k)])
                etype = float
              except:
                etype = lambda x: x
            # Evaluation
            if v[0] == '>':
              if etype(line[header.index(k)]) > etype(v[1:]):
                skip = False
            elif v[0] == '<':
              if etype(line[header.index(k)]) < etype(v[1:]):
                skip = False
            elif line[header.index(k)] == v:
                skip = False
      if skip == False:
        # Update dictionary
        ###dictionary[line[0]] = line[1:]
        # Update hierarchy
        self.hierarchy_update(line[0], indent)
        # Update hierarchy and network
        parent_name = self.hierarchy_leaf(1)
        if parent_name == None:
          parent = tree
        else:
          parent = tree.search_nodes(name=self.__wrap(parent_name))[0]

        child = parent.add_child(name=self.__wrap(line[0]))
        child.add_feature("size", "{:,}".format(int(line[header.index("Seq.")])) + "-SEQ/ " + "{:,}".format(int(line[header.index("Comb.")])) + "-COMB/ " + "{:,}".format(float(line[header.index("Area")])) + "um2")

    print (tree.get_ascii(show_internal=True, attributes=["name", "size"]))
    return

  def parse2(self, file, check):
    # Check available modules
    if not ete3_loaded:
      print ("DC_AreaReportParsing requires ETE3!")
      sys.exit(1)
    # Read file
    fcontent = f.readlines()
    # Skip header
    while fcontent[0].strip()[:len("Reference Name")] != "Reference Name":
      fcontent = fcontent[1:]
    # Process header
    header = re.split(r'\s{2,}', fcontent[0].strip())
    #print (header)
    fcontent = fcontent[2:]
    # Process content
    hierarchy = [] # contains a tuple (name, indent)
    ###dictionary = dict()
    ###nxg = nx.DiGraph()
    tree = ete3.Tree(format=1)
    for line in fcontent:
      # Extract indent
      indent = re.match(r'(\s*)', line)
      indent = len(indent.group(1))
      # Extract line columns
      line = re.split(r'\s{2,}', line.strip())
      # Check filter
      skip = True
      if len(line) == len(header):
        for k,v in check.items():
          if k in header:
            if v[0] == '>':
              if int(line[header.index(k)]) > int(v[1:]):
                skip = False
            elif v[0] == '<':
              if int(line[header.index(k)]) < int(v[1:]):
                skip = False
            elif line[header.index(k)] == v:
                skip = False
      if skip == False:
        # Update dictionary
        ###dictionary[line[0]] = line[1:]
        # Update hierarchy
        while len(hierarchy) > 0 and indent <= hierarchy[-1][1]:
          hierarchy = hierarchy[:-1]
        # Update hierarchy and network
        if len(hierarchy) == 0:
          #print (line[0])
          hierarchy.append((line[0], indent))
          child = tree.add_child(name=self.__wrap(line[0]))
          child.add_feature("size", "{:,}".format(int(line[header.index("Seq.")])) + "-SEQ/ " + "{:,}".format(int(line[header.index("Comb.")])) + "-COMB/ " + "{:,}".format(float(line[header.index("Area")])) + "um2")
        else:
          #print (hierarchy[-1][0], "-->", line[0])
          parent = tree.search_nodes(name=self.__wrap(hierarchy[-1][0]))[0]
          child = parent.add_child(name=self.__wrap(line[0]))
          child.add_feature("size", "{:,}".format(int(line[header.index("Seq.")])) + "-SEQ/ " + "{:,}".format(int(line[header.index("Comb.")])) + "-COMB/ " + "{:,}".format(float(line[header.index("Area")])) + "um2")
          ###nxg.add_edge(hierarchy[-1][0], line[0])
          hierarchy.append((line[0], indent))

    print (tree.get_ascii(show_internal=True, attributes=["name", "size"]))
    return

class DC_ElaborateLogParsing:
  def __init__(self):
    None

  def parse(self, file, check, instances, verbose):
    # Variable initialization
    counter = dict()
    pattern = []
    select = None
    table = []
    tableInfo = []
    warnings = []
    errors = []
    state = "CONTINUE"
    # Read file
    lines = f.readlines()
    for lineno, l in enumerate(lines):
      if l.startswith('Warning:'):
        warnings.append((lineno, l))
        if verbose:
          print('[W-%d] ' % lineno + lines[lineno])
      if l.startswith('Error:'):
        errors.append((lineno, l))
        if verbose:
          print('[E-%d] ' % lineno + lines[lineno])
      if state == "SKIP":
        ''' Skip a line if requested (for example next line after 'Register Name' heading is a limiting line with '=' characters '''
        state = "CONTINUE"
      elif state == "INSTANCE":
        parts = l.strip().split() # '   in routine ponip_counter_simple_15_0_3_8 line 78 in file'
        tableInfo.append({'name': parts[2], 'file': '', 'table': -1, 'instances': 1})
        state = "FILE"
      elif state == "FILE":
        l = l.strip().strip(".").strip("'")
        tableInfo[-1]['file'] = l;
        state = "CONTINUE"
      elif select == None and "Inferred memory devices in process" in l:
        state = "INSTANCE"
      elif select == None and "Information: Uniquified " in l:
        # Information: Uniquified 256 instances of design 'ponip_counter_simple_15_0_3_8'. (OPT-1056)
        parts = l.strip().split()
        ts = [t for t in tableInfo if t['name'] == parts[6].strip(".").strip("'")]
        if (len(ts) > 0):
          ts[0]['instances'] = int(parts[2])
      elif select == None:
        ''' Search for the table header pattern, if found open a new table '''
        elements = [ x.strip() for x in l.strip(' |').split('|')]
        if (elements[0] == 'Register Name'):
          table.append([])
          pattern = elements
          select = len(table) - 1
          tableInfo[-1]['table'] = select;
          state = "SKIP"
      else:
        ''' In case a table was already recognized, insert element; Close table if '=' is recognized '''
        if '=' in l:
          select = None
        else:
          elements = [ x.strip() for x in l.strip(' |').split('|')]
          table[select].append(dict(zip(pattern, elements)))
    # Build dict for instance selection
    tableInstances = {t['table']: {'instances': t['instances'], 'name': t['name']} for t in tableInfo if t['table'] != -1}
    # Build dict for name selection
    tableIdentification = {t['table']: [t['name'], t['file']] for t in tableInfo if t['table'] != -1}
    # Search for elements not matching the requirements set, store it in selection
    selection = []
    global found
    check = "if (%s): global found; found = True" % (check)
    for i, t in enumerate(table):
      ''' Iterate tables '''
      for tk, tv in enumerate(t):
        ''' Iterate table items '''
        # Consider instances
        if instances == True:
          counter_instance_name = tv['Type'] + '@' + tableInstances[i]['name']
          if counter_instance_name not in counter:
            counter[counter_instance_name] = 0
          counter[counter_instance_name] += int(tv['Width']) * tableInstances[i]['instances']
        # Calculate overall counter
        if tv['Type'] not in counter:
          counter[tv['Type']] = 0
        counter[tv['Type']] += int(tv['Width']) * tableInstances[i]['instances']
        found = False
        exec(check)
        if found:
          ''' Append entry in case it matches the search '''
          selection.append ([tv['Register Name'], {k: v for k, v in tv.items() if k != 'Register Name'}, tableIdentification[i]])
    # Find alignment and print entries
    if len(selection) > 0:
      max = 0
      for tk, tv, ti in selection:
        ''' Find alignment '''
        if len(tk) > max:
          max = len(tk)
      for tk, tv, ti in selection:
        ''' Print entries '''
        print (ti[0], tk.rjust(max), tv)
    else:
      print ('NO MATCHING ENTRIES FOUND FOR',check)
    for k, n in sorted(counter.items()):
      print ('%s count: %d' % (k, n))
    print ('Warnings: %d' % len(warnings))
    print ('Errors:   %d' % len(errors))
    return


def __filter_split(f):
  check = dict()
  for e in f.split(','):
    e0, e1 = e.split('=')
    check[e0] = e1
  return check

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-f', '--filter',
                      metavar='COLUMN=VALUE',
                      nargs='?',
                      default='',
                      help="""Filter elements of tables where the specified columns have the expected values: e.g. COLUMN=VALUE[,COLUMN=VALUE[,...]].
                              *** For *.area.rpt files these filters could look like: 'Seq.=>1000,Comb.=>1000'  ==> filters modules with Seq. > 1000 OR Comb. > 1000!
                              *** For *.log files these filters could look like:      'AR==N || AS==N'               ==> filters registers with Async.Reset==N AND Async.Set==N
                              Default='tv["AR"]=="N" or tv["AS"]=="N"' for *.log/ 'Seq.=>1000,Comb.=>1000' for *.area.rpt""")
  parser.add_argument('--instances',
                      action='store_true',
                      default=False,
                      help="""Prints sizes of all instances found (ONLY APPLICABLE TO *.log FILES).
                              Default=%(default)s""")
  parser.add_argument('--verbose', '-v',
                      action='store_true',
                      default=False,
                      help="""Prints detailed outputs (e.g.: warnings and error found in the log file).
                              Default=%(default)s""")
  parser.add_argument('inFile',
                      metavar='FILE',
                      nargs='?',
                      default='../../elaborate/elaborate_dc.log',
                      help="""DC (Synopsys DesignCompiler) Elaborate LOG File (e.g.: elaborate_dc.log) OR
                              DC (Synopsys DesignCompiler) Area Report File (e.g.: ponip_shell_16ffc.compile_incr.lvl7.area.rpt). Default=%(default)s""")
  args = parser.parse_args(sys.argv[1:])
  # Check pattern initialization

  # Open file
  f = open(args.inFile)

  # Select Parser

  if args.inFile.endswith('.rpt') and 'area' in args.inFile:
    if len(args.filter) == 0:
      args.filter = 'Seq.=>1000,Comb.=>1000'
    check = __filter_split(args.filter)
    dc_grep = DC_AreaReportParsing()
    dc_grep.parse(f, check)
  elif args.inFile.endswith('.log'):
    if len(args.filter) == 0:
      args.filter = 'tv["AR"]=="N" and tv["AS"]=="N"'
    check = args.filter #__filter_split(args.filter)
    dc_grep = DC_ElaborateLogParsing()
    dc_grep.parse(f, check, args.instances, args.verbose)

