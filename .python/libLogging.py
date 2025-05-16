__author__ = 'miedlste'

import logging
import re
import os

#
# Copyright (C) 2010-2012 Vinay Sajip. All rights reserved. Licensed under the new BSD license.
#
import ctypes
import logging
import os

class ColorizingStreamHandler(logging.StreamHandler):
    # color names to indices
    color_map = {
        'black': 0,
        'red': 1,
        'green': 2,
        'yellow': 3,
        'blue': 4,
        'magenta': 5,
        'cyan': 6,
        'white': 7,
    }

    #levels to (background, foreground, bold/intense)
    if os.name == 'nt':
        level_map = {
            logging.DEBUG: (None, 'blue', True),
            logging.INFO: (None, 'white', False),
            logging.WARNING: (None, 'yellow', True),
            logging.ERROR: (None, 'red', True),
            logging.CRITICAL: ('red', 'white', True),
        }
    else:
        level_map = {
            logging.DEBUG: (None, 'blue', False),
            logging.INFO: (None, 'black', False),
            logging.WARNING: (None, 'yellow', False),
            logging.ERROR: (None, 'red', False),
            logging.CRITICAL: ('red', 'white', True),
        }
    csi = '\x1b['
    reset = '\x1b[0m'

    @property
    def is_tty(self):
        isatty = getattr(self.stream, 'isatty', None)
        return isatty and isatty()

    def emit(self, record):
        try:
            message = self.format(record)
            stream = self.stream
            if not self.is_tty:
                stream.write(message)
            else:
                self.output_colorized(message)
            stream.write(getattr(self, 'terminator', '\n'))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    if os.name != 'nt':
        def output_colorized(self, message):
            self.stream.write(message)
    else:
        import re
        ansi_esc = re.compile(r'\x1b\[((?:\d+)(?:;(?:\d+))*)m')

        nt_color_map = {
            0: 0x00,    # black
            1: 0x04,    # red
            2: 0x02,    # green
            3: 0x06,    # yellow
            4: 0x01,    # blue
            5: 0x05,    # magenta
            6: 0x03,    # cyan
            7: 0x07,    # white
        }

        def output_colorized(self, message):
            parts = self.ansi_esc.split(message)
            write = self.stream.write
            h = None
            fd = getattr(self.stream, 'fileno', None)
            if fd is not None:
                fd = fd()
                if fd in (1, 2): # stdout or stderr
                    h = ctypes.windll.kernel32.GetStdHandle(-10 - fd)
            while parts:
                text = parts.pop(0)
                if text:
                    write(text)
                if parts:
                    params = parts.pop(0)
                    if h is not None:
                        params = [int(p) for p in params.split(';')]
                        color = 0
                        for p in params:
                            if 40 <= p <= 47:
                                color |= self.nt_color_map[p - 40] << 4
                            elif 30 <= p <= 37:
                                color |= self.nt_color_map[p - 30]
                            elif p == 1:
                                color |= 0x08 # foreground intensity on
                            elif p == 0: # reset to default color
                                color = 0x07
                            else:
                                pass # error condition ignored
                        ctypes.windll.kernel32.SetConsoleTextAttribute(h, color)

    def colorize(self, message, record):
        if record.levelno in self.level_map:
            bg, fg, bold = self.level_map[record.levelno]
            params = []
            if bg in self.color_map:
                params.append(str(self.color_map[bg] + 40))
            if fg in self.color_map:
                params.append(str(self.color_map[fg] + 30))
            if bold:
                params.append('1')
            if params:
                message = ''.join((self.csi, ';'.join(params),
                                   'm', message, self.reset))
        return message

    def format(self, record):
        message = logging.StreamHandler.format(self, record)
        if self.is_tty:
            # Don't colorize any traceback
            #parts = message.split('\n', 1)
            #parts[0] = self.colorize(parts[0], record)
            #message = '\n'.join(parts)
            message = self.colorize(message, record)
        return message

class libLogging:
    logfile = None
    logfile_nocolor = True
    libinfo = None
    libcore = None
    ext = None
    tty_rows = 0
    tty_columns = 0
    console = None

    @classmethod
    def __init__(cls, logfile = None):
        tty_config = os.popen('stty size', 'r').read().split()
        cls.tty_rows, cls.tty_columns = int(tty_config[0]), int(tty_config[1]) - (8 + 5 + 4)
        # Set up logging to file
        cls.logfile = logfile
        if logfile is not None:
            #logging.basicConfig(#level=logging.INFO,
                        #format='[%(asctime)s@%(module)20s(%(lineno)3d): %(levelname)8s@%(name)-5s] %(message)s',
                        #datefmt='%m/%d %H:%M')
                        #filename=logfile,
                        #filemode='w')
            cls.lib_logfile = logging.FileHandler(logfile, mode='w')
            formatter = logging.Formatter('[%(asctime)s@%(module)20s(%(lineno)3d): %(levelname)8s@%(name)-5s] %(message)s',
                                          datefmt='%m/%d %H:%M')
            cls.lib_logfile.setFormatter(formatter)
            cls.lib_logfile.setLevel(logging.INFO)
        # set a format which is simpler for console use
        formatter = logging.Formatter('[%(levelname)8s@%(name)-5s] %(message)s',
                                      datefmt='%m/%d %H:%M')
        # define a Handler which writes INFO messages or higher to the sys.stderr
        #cls.console = logging.StreamHandler()
        #cls.console.setLevel(logging.DEBUG)
        # tell the handler to use this format
        #cls.console.setFormatter(formatter)
        # add the handler to the root logger
        #logging.getLogger('').addHandler(cls.console)

        ############################################
        # Create lib Core logging
        cls.libinfo = logging.getLogger('libI')
        cls.libinfo.setLevel(logging.DEBUG)
        cls.libinfo_console = ColorizingStreamHandler() #logging.StreamHandler()
        cls.libinfo_console.setFormatter(formatter)
        cls.libinfo_console.setLevel(logging.INFO)
        cls.libinfo.addHandler(cls.libinfo_console)
        if cls.lib_logfile is not None:
            cls.libinfo.addHandler(cls.lib_logfile)
        ############################################
        # Create external logging
        cls.libcore = logging.getLogger('libC')
        cls.libcore.setLevel(logging.DEBUG)
        cls.libcore_console = ColorizingStreamHandler() #logging.StreamHandler()
        cls.libcore_console.setFormatter(formatter)
        cls.libcore_console.setLevel(logging.WARNING)
        cls.libcore.addHandler(cls.libcore_console)
        if cls.lib_logfile is not None:
            cls.libcore.addHandler(cls.lib_logfile)
        ############################################
        # Create external logging
        cls.ext = logging.getLogger('EXT')
        cls.ext.setLevel(logging.DEBUG)
        cls.libext_console = ColorizingStreamHandler() #logging.StreamHandler()
        cls.libext_console.setFormatter(formatter)
        cls.libext_console.setLevel(logging.WARNING)
        cls.ext.addHandler(cls.libext_console)
        if cls.lib_logfile is not None:
            cls.ext.addHandler(cls.lib_logfile)
        return

    @classmethod
    def setLevel(cls, level):
        #logging.getLogger('').setLevel(level)
        #cls.console.setLevel(level)
        return

    @classmethod
    def logfile_cleanup(cls):
        logging.shutdown()
        if cls.logfile_nocolor and cls.logfile is not None:
            wcontent = ''
            f = open(cls.logfile, 'r')
            pattern = re.compile(r'\x1b\[[;0-9]*m')
            for line in f.readlines():
                line = re.subn(pattern, '', line)
                wcontent += line[0]
            f.close()
            f = open(cls.logfile, 'w')
            f.write(wcontent)
            f.close()

    #@classmethod
    #def libinfo_debug(cls, msg, *args, **kwargs):
    #    cls.libinfo.debug(msg, *args, **kwargs)
    #    return
    #
    #@classmethod
    #def libinfo_info(cls, msg, *args, **kwargs):
    #    cls.libinfo.info(msg, *args, **kwargs)
    #    return
    #
    #@classmethod
    #def libinfo_warning(cls, msg, *args, **kwargs):
    #    cls.libinfo.warning(msg, *args, **kwargs)
    #    return
    #
    #@classmethod
    #def libinfo_error(cls, msg, *args, **kwargs):
    #    cls.libinfo.error(msg, *args, **kwargs)
    #    return
    #
    #@classmethod
    #def libinfo_critical(cls, msg, *args, **kwargs):
    #    cls.libinfo.critical(msg, *args, **kwargs)
    #    return

    #########################################################

    #@classmethod
    #def libcore_debug(cls, msg, *args, **kwargs):
    #    cls.libcore.debug(msg, *args, **kwargs)
    #    return
    #
    #@classmethod
    #def libcore_info(cls, msg, *args, **kwargs):
    #    cls.libcore.info(msg, *args, **kwargs)
    #    return
    #
    #@classmethod
    #def libcore_warning(cls, msg, *args, **kwargs):
    #    cls.libcore.warning(msg, *args, **kwargs)
    #    return
    #
    #@classmethod
    #def libcore_error(cls, msg, *args, **kwargs):
    #    cls.libcore.error(msg, *args, **kwargs)
    #    return
    #
    #@classmethod
    #def libcore_critical(cls, msg, *args, **kwargs):
    #    cls.libcore.critical(msg, *args, **kwargs)
    #    return

    #########################################################

    @classmethod
    def ext_debug(cls, msg, *args, **kwargs):
        cls.ext.debug(msg, *args, **kwargs)
        return

    @classmethod
    def ext_info(cls, msg, *args, **kwargs):
        cls.ext.info(msg, *args, **kwargs)
        return

    @classmethod
    def ext_warning(cls, msg, *args, **kwargs):
        cls.ext.warning(msg, *args, **kwargs)
        return

    @classmethod
    def ext_error(cls, msg, *args, **kwargs):
        cls.ext.error(msg, *args, **kwargs)
        return

    @classmethod
    def ext_critical(cls, msg, *args, **kwargs):
        cls.ext.critical(msg, *args, **kwargs)
        return
