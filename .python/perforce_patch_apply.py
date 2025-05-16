import os
import sys
import argparse
import re
import subprocess

class FileManagement:
    def __init__(self, p4=False, dryrun=False):
        self.p4 = p4
        self.dryrun = dryrun
        self.edit_list = []

    def exec(self, cmd):
        if self.dryrun:
            print('$ ' + " ".join(cmd))
        else:
            print('$ ' + " ".join(cmd))
            if sys.version_info >= (3, 5):
                subprocess.run(cmd)
            else:
                subprocess.call(cmd)

    def check(self, filepath):
        if os.path.exists(filepath):
            return True
        else:
            print("ERROR: File does not exist '%s'"%(filepath))
            return False

    def edit(self, filepath):
        if filepath not in self.edit_list and self.check(filepath):
            if self.p4:
                if os.path.isdir(filepath):
                    filepath += '/...'
                self.exec(['p4', 'edit', filepath])
            else:
                self.exec(['chmod', '+w', filepath])
            self.edit_list.append(filepath)

    def move(self, dst, src):
        if self.check(src):
            self.edit(src)
            if self.p4:
                if os.path.isdir(src):
                    src += '/...'
                    dst += '/...'
                self.exec(['p4', 'move', src, dst])
            else:
                self.exec(['mv', src, dst])

    def txtreplace(self, filepath, mapping):
        if self.check(filepath):
            txtnew = None
            with open(filepath, 'rb') as f:
                try:
                    txtorig = f.read().decode()
                    count = 0
                    for src, dst in mapping.items():
                        txtnew, count_single = re.subn(src, dst, txtorig)
                        txtorig = txtnew
                        count += count_single
                        if count_single > 0:
                            print("Replace text in file '%s' (%s --> %s)" % (filepath, src, dst))
                except Exception as e:
                    print("ERROR [%s] replacing text in file '%s'" % (e, filepath))
            if txtnew is not None and count > 0:
                self.edit(filepath)
                if not self.dryrun:
                    try:
                        with open(filepath, 'w') as f:
                            f.write(txtnew)
                    except UnicodeEncodeError:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(txtnew)
                    except Exception as e:
                        print(e)

class PerforcePatchApply:
    def __init__(self, p4=False, dryrun=False):
        self.fm = FileManagement(p4, dryrun)
        self.dryrun = dryrun
        self.mapping = None
        self.filelist = []
        self.filelist_target = []
        self.patch_files_new = []

    def print_filelist(self, header, filelist):
        print(header)
        for f in filelist:
            print(' '*4 + '-- %s'%f)

    def find_files_to_patch(self, patch_files):
        regex_minus = re.compile(r'--- /(/\w+)*/[\w\.]+')
        regex_plus = re.compile(r'\+\+\+ /(/\w+)*/[\w\.]+')
        self.filelist = []
        for pf in patch_files:
            if os.path.exists(pf) and os.path.isfile(pf):
                with open(pf) as f:
                    lines = f.readlines()
                    for nr, line in enumerate(lines):
                        match = regex_minus.match(line)
                        if match is not None:
                            match = regex_plus.match(lines[nr + 1])
                            if match is not None:
                                self.filelist.append(match.group()[4:])
        return self.filelist

    def generate_new_patchfiles(self, patch_files):
        self.patch_files_new = []
        for pf in patch_files:
            with open(pf) as f:
                content = f.read()
            if content is not None:
                for nr, path_from in enumerate(self.filelist):
                    print("%s --> %s"%(path_from, self.filelist_target[nr]))
                    content = content.replace("--- " + path_from, "--- " + self.filelist_target[nr])
                    content = content.replace("+++ " + path_from, "+++ " + self.filelist_target[nr])
                new_path_path = os.path.join("/tmp", os.path.basename(pf)) + ".%d"%(hash(pf))
                with open(new_path_path, 'w') as f:
                    f.write(content)
                    f.close()
                    self.patch_files_new.append(new_path_path)

    def check_root_in_paths(self, root, filelist):
        for f in filelist:
            if root != f[0:len(root)]:
                print("ERROR: root path '%s' not applicable to all affected files!"%root)
                return False
        return True

    def check_new_path_exist(self, path_from, path_to, filelist):
        self.filelist_target = []
        for f in filelist:
            f_new = path_to + f[len(path_from):]
            if self.fm.check(f_new) is False:
                self.filelist_target = []
                return False
            else:
                self.filelist_target.append(f_new)
        return True

    def input_paths(self):
        path_from_ok = False
        path_to_ok = False
        while path_from_ok is False:
            path_from = input("Please tell me the root of the path you want to replace: ")
            path_from_ok = self.check_root_in_paths(path_from, self.filelist)
        while path_to_ok is False:
            path_to = os.path.expandvars(input("Please tell me the new root path: "))
            path_to_ok = self.check_new_path_exist(path_from, path_to, self.filelist)

    def apply_patch(self):
        print("Making files editable ...")
        for f in self.filelist_target:
            self.fm.edit(f)
        print("Patching files ...")
        for pf in self.patch_files_new:
            print('Run the following command (example): ' + ' '.join(["patch", '-u', "-p8", "--merge", "-i" + pf]))
            #self.fm.exec(["patch", '-u', "-p8", "-i" + pf])


if __name__ == '__main__':
    if sys.version_info < (3, 0):
        raise "You must use python 3.x or greater!"

    parser = argparse.ArgumentParser()
    parser.add_argument('--p4', action='store_true', default=False, help="Use perforce")
    parser.add_argument('-n', '--dryrun', action='store_true', default=False, help="Don't execute, just print")
    parser.add_argument('-m', '--map', action='store', nargs='+', default=None, help="Mapping file(s) or mapping enties. As separator : are assumed (within a file whitespaces are ignored). Example: <old-name>:<new-name>")
    parser.add_argument('-p', '--patch', action='store', nargs='+', default=None, help="Patch file(s) to be processes")

    if len(sys.argv) < 2:
        parser.print_help()
    else:
        presult = parser.parse_args()
        #presult = vars(presult)

        main = PerforcePatchApply(presult.p4, presult.dryrun)
        filelist = main.find_files_to_patch(presult.patch)

        #for file in filelist:
        #    print(file)

        main.print_filelist('Files to be patched (original):', filelist)
        main.input_paths()
        main.print_filelist('Files to be patched (local):', main.filelist_target)
        main.generate_new_patchfiles(presult.patch)
        main.apply_patch()

