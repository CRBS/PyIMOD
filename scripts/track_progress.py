#!/usr/bin/env python

from __future__ import division

import sys
import os
import datetime
import pyimod
from optparse import OptionParser

def parse_args():
    global p
    p = OptionParser(usage = "%prog [options] /path/to/model /path/to/csv")
    (opts, args) = p.parse_args()
    fileModel, fileCSV = check_args(args)
    return opts, fileModel, fileCSV

def check_args(args):
    if len(args) is not 2:
        usage("Improper number of arguments.")
    fileModel = args[0]
    fileCSV = args[1]
    if not os.path.isfile(fileModel):
        usage("{0} is not a valid file".format(fileModel))
    return fileModel, fileCSV

# Print error messages and exit
def usage(errstr):
    print ""
    print "ERROR: {0}".format(errstr)
    print ""
    p.print_help()
    print ""
    exit(1)

if __name__ == '__main__':
    opts, fileModel, fileCSV = parse_args()

    fid = open(fileCSV, 'a')

    # Get time and date data
    strDate = str(datetime.datetime.now())
    date, time = strDate.split()

    # Get filesize in MB
    fileSize = float(os.path.getsize(fileModel))
    fileSize = fileSize / (1e6)

    # Load IMOD model into pyimod and extract pertinent data
    mod = pyimod.ImodModel(fileModel)
    nObjects = mod.nObjects
    nContours = 0
    for N in range(nObjects):
        nContours = nContours + mod.Objects[N].nContours

    # Write basic data on the model file
    fid.write('{0},{1},{2},{3},{4}'.format(date, time, fileSize, nObjects, nContours))

    fid.close()        

