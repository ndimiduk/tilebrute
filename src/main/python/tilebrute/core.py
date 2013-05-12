
import os
from sys import stderr

# hadoop helpers

def print_status(msg):
    print >> stderr, "reporter:status:%s" % msg

def inc_counter(group, counter, inc=None):
    if not inc:
        inc = 1
    print >> stderr, "reporter:counter:%s,%s,%d" % (group, counter, inc)

def emit(key, val):
    print "%s\t%s" % (key, val)

# utils

# from http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python/377028#377028
def which(program):
    """Locate an executable on the system path.
    """
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

# spherical mercator
merc_srs = '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over<>'
