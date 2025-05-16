import os
import sys
import argparse
import re
import subprocess
from typing import Any, Iterable, Optional

def colored_dummy(text: str, color: Optional[str] = None, on_color: Optional[str] = None, attrs: Optional[Iterable[str]] = None,) -> str:
    return text

try:
    from termcolor import colored
    colorize = colored
except:
    colorize = colored_dummy


class Log:
    INFO = 2
    WARNING = 1
    ERROR = 0
    PRINT = -1
    verbosity = INFO

    def __init__(self):
        pass

    @classmethod
    def set_verbosity(cls, verbosity):
        cls.verbosity = verbosity

    @classmethod
    def print(cls, severity, msg, *args, **kwargs):
        if severity <= cls.verbosity:
            if severity == cls.ERROR:
                msg = colorize("[E] " + msg, 'red')
            elif severity == cls.WARNING:
                msg = colorize("[W] " + msg, 'yellow')
            elif severity == cls.INFO:
                msg = colorize("[I] " + msg, 'blue')
            else:
                msg = colorize("    " + msg)

            print(msg, *args, **kwargs)


class FileManagement:
    def __init__(self, p4=False, dryrun=False):
        self.p4 = p4
        self.dryrun = dryrun
        self.edit_list = []

    def exec(self, cmd):
        if self.dryrun:
            Log.print(Log.PRINT, '$ ' + " ".join(cmd))
        else:
            Log.print(Log.PRINT, '$ ' + " ".join(cmd))
            if sys.version_info >= (3, 5):
                subprocess.run(cmd)
            else:
                subprocess.call(cmd)

    def check(self, filepath):
        if os.path.exists(filepath):
            return True
        else:
            Log.print(Log.ERROR, "File does not exist '%s'"%(filepath))
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
                            Log.print(Log.PRINT, "Replace text in file '%s' (%s --> %s)" % (filepath, src, dst))
                except Exception as e:
                    Log.print(Log.WARNING, "[%s] replacing text in file '%s'" % (e, filepath))
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
                        Log.print(Log.ERROR, e)

class BatchRename:
    def __init__(self, p4=False, dryrun=False, wordonly=True):
        self.fm = FileManagement(p4, dryrun)
        self.wordonly = wordonly
        self.mapping = None

    def extract_mapping_from_txt(self, txt, separator):
        txt = txt.strip()
        if txt.startswith('#') or txt.startswith('//'):
            txt = ''
        if len(txt) > 0:
            elements = txt.split(separator)
            if len(elements) == 2:
                elements = [e.strip() for e in elements]
                if elements[0] in self.mapping.keys():
                    Log.print(Log.ERROR, "Mapping source defined multiple times '%s'" % (elements[0]))
                    #sys.exit(-1)
                if elements[1] in self.mapping.values():
                    Log.print(Log.ERROR, "Mapping destination defined multiple times '%s'" % (elements[1]))
                    #sys.exit(-1)
                if elements[0] == elements[1]:
                    Log.print(Log.WARNING, "Mapping from/to is EQUAL to '%s' --> NO MAPPING DONE" % (elements[1]))
                else:
                    if self.wordonly:
                        elements[0] = r'\b' + elements[0] + r'\b'
                    self.mapping[elements[0]] = elements[1]
            else:
                Log.print(Log.ERROR, "This is not a correct mapping '%s'" % (txt))
        return None

    def read_mapping_from_file(self, mapping_input, separator=':'):
        if (os.path.exists(mapping_input)):
            with open(mapping_input) as f:
                for l in f.readlines():
                    self.extract_mapping_from_txt(l, separator)
            return None

    def read_mapping(self, mapping_input, separator=':'):
        self.mapping = {}
        for m in mapping_input:
            if (os.path.isfile(m)):
                self.read_mapping_from_file(m, separator)
            else:
                self.extract_mapping_from_txt(m, separator)
        return self.mapping

    def print_mapping(self, mapping):
        Log.print(Log.PRINT, "MAPPING TABLE")
        for k, i in mapping.items():
            Log.print(Log.PRINT, "%s --> %s"%(k, i))

    def search_files_and_dirs(self, directory='.', extension=''):
        extension = extension.lower()
        filelist = []
        dirlist = set()
        for dirpath, dirnames, files in os.walk(directory):
            for name in files:
                if extension and name.lower().endswith(extension):
                    filelist.append(os.path.abspath(os.path.join(dirpath, name)))
                elif not extension:
                    filelist.append(os.path.abspath(os.path.join(dirpath, name)))
            for name in dirnames:
                dirlist.add(os.path.join(dirpath, name))
        return filelist, dirlist

    def grep_files_and_dirs(self, objects):
        filelist = []
        dirlist = set()
        for o in objects:
            if os.path.isdir(o):
                dirlist.update(o)
                fl, dl = self.search_files_and_dirs(o)
                filelist += fl
                dirlist.update(dl)
            elif os.path.isfile(o):
                filelist.append(os.path.abspath(o))
                dirlist.add(os.path.dirname(o))
        return filelist, dirlist

    def replace_txt_in_files(self, filelist, mapping):
        for f in filelist:
            self.fm.txtreplace(f, mapping)

    def rename_files(self, filelist, mapping):
        keys = mapping.keys()
        for f in filelist:
            dirname = os.path.dirname(f)
            basename, ext = os.path.splitext(os.path.basename(f))
            key = None
            for k in keys:
                testobj = re.search(k, basename)
                if testobj is not None:
                    key = k
                    break
            if key is not None:
                basename_new, count = re.subn(key, mapping[key], basename)
                dst = os.path.join(dirname, basename_new)
                dst += ext
                self.fm.move(dst, f)

    def rename_dirs(self, dirlist, mapping):
        keys = mapping.keys()
        for d in dirlist:
            dirname = os.path.dirname(d)
            basename = os.path.basename(d)
            key = None
            for k in keys:
                testobj = re.search(k, basename)
                if testobj is not None:
                    key = k
                    break
            if key is not None:
                basename_new, count = re.subn(key, mapping[key], basename)
                dst = os.path.join(dirname, basename_new)
                self.fm.move(dst, d)


if __name__ == '__main__':
    if sys.version_info < (3, 0):
        raise "You must use python 3.x or greater!"

    parser = argparse.ArgumentParser()
    parser.add_argument('--p4', action='store_true', default=False, help="Use perforce")
    parser.add_argument('-v', '--verbosity', action='store', type=int, default=Log.ERROR, help="Verbosity Level (0-2)")
    parser.add_argument('-n', '--dryrun', action='store_true', default=False, help="Don't execute, just print")
    parser.add_argument('-m', '--map', action='store', nargs='+', required=True, default=None, help="Mapping file(s) or mapping enties. As separator : are assumed (within a file whitespaces are ignored). Example: <old-name>:<new-name>")
    parser.add_argument('-w', '--word-only', action='store_true', default=False, help="Consider words only. Like the perl/python regex \\b")
    parser.add_argument('--separator', action='store', default=':', help="Separator between the 'from/to' mapping. Default: %(default)s")
    parser.add_argument('-d', '--dirname', action='store_true', default=False, help="Rename directories")
    parser.add_argument('-f', '--filename', action='store_true', default=False, help="Rename files")
    parser.add_argument('-c', '--filecontent', action='store_true', default=False, help="Rename file content")
    parser.add_argument('-o', '--object', action='store', nargs='+', required=True, default=None, help="A file or directory where the operation has to be executed.")
    parser.add_argument('--filefilter', action='store', default=None, help="Perl regular expression filter for the files found within the OBJECT (dirs/files)")
    parser.add_argument('--nocolor', action='store_true', default=False, help="No coloring of outputs")


    if len(sys.argv) < 2:
        parser.print_help()
    else:
        presult = parser.parse_args()
        #presult = vars(presult)

        Log.set_verbosity(presult.verbosity)
        if presult.nocolor is True:
            colorize = colored_dummy

        main = BatchRename(presult.p4, presult.dryrun, presult.word_only)
        filelist, dirlist = main.grep_files_and_dirs(presult.object)

        if presult.filefilter is not None:
            regex = presult.filefilter
            filelist = [f for f in filelist if re.match(regex, f, re.I)]

        #for f in filelist:
        #    print(f)

        mapping = main.read_mapping(presult.map, presult.separator)

        #main.print_mapping(mapping)

        ###############################
        ## RENAMING/ REPLACING
        if presult.filecontent:
            Log.print(Log.PRINT, "Replace file content ...")
            main.replace_txt_in_files(filelist, mapping)
        if presult.filename:
            Log.print(Log.PRINT, "Rename files ...")
            main.rename_files(filelist, mapping)
        if presult.dirname:
            Log.print(Log.PRINT, "Rename directories ...")
            main.rename_dirs(dirlist, mapping)
        if not presult.filecontent and not presult.filename and not presult.dirname:
            Log.print(Log.ERROR, "No replacing/renaming selected!")