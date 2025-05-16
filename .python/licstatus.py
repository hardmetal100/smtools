import sys
import os
import re
import subprocess
import time
import argparse

class LicenseStatus:
    def __init__(self, lifetime):
        self.server = ""
        self.files = []
        self.licstmpfile = ".lmstat.rpt"
        self.licstmpfile_lifetime = lifetime # seconds
        self.licsraw = ""
        self.lics = {}
        self.licname_max = 0
        self.usrname_max = 0
        return

    def lic_query(self, server_list, tool):
        if os.path.exists(self.licstmpfile) and (time.time() - os.path.getmtime(self.licstmpfile)) < self.licstmpfile_lifetime:
            #print ("Time of last file update: %d"%(os.path.getmtime(self.licstmpfile)))
            #print ("Time now:                 %d"%(time.time()))
            #print ("Time diff:                %d"%(time.time() - os.path.getmtime(self.licstmpfile)))
            f = open(self.licstmpfile)
            self.licsraw = f.read() + "\n"
            f.close()
        else:
            for s in server_list:
                print ("Query Server(s) '%s'"%(s))
                result = subprocess.run(tool.split() + ["-a", "-c", s], stdout=subprocess.PIPE)
                self.licsraw += result.stdout.decode(encoding=sys.getdefaultencoding(), errors='ignore') + "\n"
            try:
                f = open(self.licstmpfile, 'w')
                f.write(self.licsraw)
                f.close()
            except:
                None
        return

    def lic_extract(self):
        # yangshi1 sinrse0031               sinrsa0006.isng.phoenix.local:7.0                       (v13.100) (radon.maxlinear.com/5280 4888), start Tue 12/1 8:29
        # amashrak tlvrsf0020               tlvrsa0009.iil.intel.com:8.0 Xcelium Single Core Engine (v20.000) (radon.maxlinear.com/5280 35517), start Wed 12/2 12:43
        # arkin    tlvrsf0014.iil.intel.com tlvrsa0009.iil.intel.com:17.0 ACD2064331556             (v20.0)   (radon.maxlinear.com/5280 9001), start Tue 12/1 5:00
        # kuahhsia                          kuahhsia-MOBL1 0:0                                      (v17.200) (neon.maxlinear.com/5280 18953), start Thu 12/3 9:51
        # Regular Expression Compiles
        re_server = re.compile("\s*License server Status: ([0-9@.a-z]+).*", re.IGNORECASE)
        re_lic_title = re.compile("\s*Users of ([^:]+):\s*\(Total of (\d+) license[s]? issued;\s*Total of (\d+) license[s]? in use\)", re.IGNORECASE)
        re_lic_users = re.compile("\s*(?P<user>[\w\d]+)\s+(?P<comment>[^\(]+)\((?P<version>[\d\w\.]+)\)\s+\([^\)]+\),?\s+(?P<status>.+)", re.IGNORECASE)
        #re_lic_users = re.compile("\s*(?P<user>[\w\d]+)\s+(?P<machine>[\w\d:\.]+)\s+(?P<display>[\w\d:\.]+)(?P<comment>[^\(]+)\((?P<version>[\d\w\.]+)\)\s+\([^\)]+\),?\s+(?P<status>.+)", re.IGNORECASE)

        for l in self.licsraw.splitlines():
            # Check User
            re_match = re_lic_users.match(l)
            # print ("check user ...")
            if re_match:
                #print ("match")
                if re_match.group("user") not in ls.lics[current_lic]["users"]:
                    if len(re_match.group("user")) > self.usrname_max:
                        self.usrname_max = len(re_match.group("user"))
                    self.lics[current_lic]["users"][re_match.group("user")] = 1
                else:
                    self.lics[current_lic]["users"][re_match.group("user")] += 1
            else:
                #print (l)
                # Check Server
                re_match = re_server.match(l)
                if re_match:
                    self.server = re_match.group(1)
                else:
                    # Check Title
                    re_match = re_lic_title.match(l)
                    if re_match:
                        current_lic = re_match.group(1)
                        if len(current_lic) > self.licname_max:
                            self.licname_max = len(current_lic)
                        if current_lic not in self.lics:
                            self.lics[current_lic] = {"overview": (0, 0)}
                            self.lics[current_lic]["users"] = {}
                        self.lics[current_lic]["overview"] = (self.lics[current_lic]["overview"][0] + int(re_match.group(3)),
                                                              self.lics[current_lic]["overview"][1] + int(re_match.group(2)))       
        return

    def lic_print(self, fltr_lics=None, fltr_min_used=0, fltr_min_avail=0, fltr_max_free=100000):
        for k, v in self.lics.items():
            match_fltr_lics = not fltr_lics or re.search(fltr_lics, k, re.IGNORECASE) is not None
            match_fltr_min_used = v["overview"][0] >= fltr_min_used
            match_fltr_min_avail = v["overview"][1] >= fltr_min_avail
            match_fltr_max_free = (v["overview"][1] - v["overview"][0]) < fltr_max_free
            
            if match_fltr_lics and match_fltr_min_used and match_fltr_min_avail and match_fltr_max_free:
                print (k.ljust(self.licname_max), ": ", "%s/%s"%(v["overview"][0], v["overview"][1]))
                n = len(v["users"].items()) - 1
                #print ("|".rjust(self.licname_max + 2) + "-".ljust(self.licname_max, "-"))
                #a = numpy.array(list(v["users"].items()))
                #a_sort = a[a[:,1].argsort()]
                a = list(v["users"].items())
                try:
                    a_sort = sorted(a, key=lambda x: x[1], reverse=True)
                except:
                    a_sort = []
                for i, (u, cnt) in enumerate(a_sort):
                    if i != n:
                        print("|--".rjust(self.licname_max + 4), u.ljust(self.usrname_max), ": ", "%s"%(cnt))
                    else:
                        print("`--".rjust(self.licname_max + 4), u.ljust(self.usrname_max), ": ", "%s"%(cnt))
        return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Licencse Status Representation based on lmstat.')
    parser.add_argument('--flt_lics',
                        nargs='?',
                        metavar='REGEX',
                        default='',
                        help="""Filter for licenses based on Python/Perl regular expressions (case is ignored). E.g.: '(assembler|explorer)' presents all licenses having assembler or explorer in its name. Default='' which shows all lics""")
    parser.add_argument('--flt_min_used',
                        nargs='?',
                        type=int,
                        default=0,
                        help="""Filter for licenses with a minimum of used licenses. Default=%(default)s""")
    parser.add_argument('--flt_min_avail',
                        nargs='?',
                        type=int,
                        default=0,
                        help="""Filter for licenses with a minimum of available licenses. Default=%(default)s""")
    parser.add_argument('--flt_max_free',
                        nargs='?',
                        type=int,
                        default=100000,
                        help="""Filter for licenses with a maximum of free licenses (e.g. to filter for lics where none is free, set this to 0). Default=%(default)s""")
    parser.add_argument('-s', '--servers',
                        nargs='?',
                        default=os.environ["CDS_LIC_FILE"],
                        help="""Contact the following license port@servers (default uses the CDS_LIC_FILE environment variable). Default=%(default)s""")
    parser.add_argument('-t', '--lifetime',
                        nargs='?',
                        type=int,
                        default=120,
                        help="""Lifetime of a previous server request in seconds (so no need to do a timely request again if within the lifetime). Default=%(default)s""")
    parser.add_argument('--tool',
                        default="lmstat",
                        help="""Tool to be used to fetch the licdata. Default=%(default)s""")

    args = parser.parse_args()
    #print(args.accumulate(args.integers))

    ls = LicenseStatus(args.lifetime)

    #server_list = [
    #    os.environ["CDS_LIC_FILE"],        #"5280@radon.maxlinear.com", "5280@neon.maxlinear.com", # CADENCE
    #    os.environ["SNPSLMD_LICENSE_FILE"] #"7737@radon.maxlinear.com", "7737@neon.maxlinear.com"  # SYNOPSYS
    #    ]
    #license_list = "(xcelium|incisive)"
    #license_list = "(assembler|explorer)"
    #license_list = ""
    
    # Processing
    ls.lic_query([args.servers], args.tool)
    ls.lic_extract() 
    ls.lic_print(fltr_lics=args.flt_lics, fltr_min_used=args.flt_min_used, fltr_min_avail=args.flt_min_avail, fltr_max_free=args.flt_max_free)
        
    
