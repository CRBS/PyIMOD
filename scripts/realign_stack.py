#!/usr/bin/env python

"""
Realigns an MRC stack based on points placed in an IMOD model file. This is used
to correct big translational jumps from one slice to another. To build the model
file, create a scattered point object. Place one point on the slice before the
jump, and the next point on the slice after the jump, with each point placed on
a new contour. For example, if a dendrite is being aligned, place one point in
the center of the dendrite on the slice before and after the jump, resulting in
two contours with one point on each. This can be repeated for as many jumps as
are in the MRC stack.

Optionally, an IMOD model file containing traces built on the input MRC stack
can also be realigned to the realigned stack using the --modelIn and --modelOut
flags.
"""

import os
import pyimod
import subprocess
from optparse import OptionParser

def parse_args():
    global p
    p = OptionParser(usage = "%prog [options] file.mod file_in.mrc file_out.mrc")
    p.add_option('--modelIn',
                dest = 'modelIn', 
                metavar = 'FILE',
                help = 'Name of a model file to align to the realigned stack.')
    p.add_option('--modelOut',
                dest = 'modelOut',
                metavar = 'FILE',
                help = 'Output name for realigned model file.')
    (opts, args) = p.parse_args()
    file_mod, file_mrc, file_out = check_args(args)
    return opts, file_mod, file_mrc, file_out

def check_args(args):
    if len(args) is not 3:
        usage("Improper number of arguments.")
    file_mod = args[0]
    file_mrc = args[1]
    file_out = args[2]

    if not os.path.isfile(file_mod):
        usage("{0} is not a valid file".format(file_mod))

    if not os.path.isfile(file_mrc):
        usage("{0} is not a valid file".format(file_mrc))

    pathsplit, dirsplit = os.path.split(file_out)
    if not pathsplit:
        pathsplit = '.'
    if not os.path.isdir(pathsplit):
        usage("The path {0} does not exist".format(file_out))

    return file_mod, file_mrc, file_out

def usage(errstr):
    print ""
    print "ERROR: {0}".format(errstr)
    print ""
    p.print_help()
    print ""
    exit(1)

if __name__ == '__main__':
    opts, file_mod, file_mrc, file_out = parse_args()

    # Check the --modelIn and --modelOut options. If --modelOut is not given,
    # append '.realigned' to the input file name.
    if opts.modelIn and not opts.modelOut:
        opts.modelOut = opts.modelIn + '.realigned'
    if opts.modelOut and not opts.modelIn:
        usage("Must specify an input model with --modelIn")
    
    # Load the scattered point model.
    mod = pyimod.ImodModel(file_mod)

    # Get listing of z values for realignment
    ncont = mod.Objects[0].nContours
    zlist = []
    for iCont in range(ncont):
        zlist.append(mod.Objects[0].Contours[iCont].points[2]) 
    zlist.append(mod.zMax)

    # Loop over all z values. Open a new .xf file, and write the appropriate
    # line for each slice. Translational values are stored to the 5th and 6th
    # values on each line for the X and Y translations, respectively.
    C = 0
    dx = 0
    dy = 0
    fid = open('realign.xf', 'a+')
    for i in range(zlist[-1]):
        if i < zlist[C]:
            strwrite = '1 0 0 1 {0} {1}\n'.format(dx, dy)
        elif i == zlist[C]:
            strwrite = '1 0 0 1 {0} {1}\n'.format(dx, dy)
            pt1 = mod.Objects[0].Contours[C].points
            pt2 = mod.Objects[0].Contours[C+1].points
            dx = -(pt2[0] - pt1[0]) + dx
            dy = -(pt2[1] - pt1[1]) + dy
            C += 2
        fid.write(strwrite)
    fid.close()

    # Run newstack command to align based on the stored .xf file.
    cmd = 'newstack -xform realign.xf {0} {1}'.format(file_mrc, file_out)
    subprocess.call(cmd.split())

    # (OPTIONAL) Run xfmodel to realign input model to the output MRC stack
    if opts.modelIn:
        cmd = 'xfmodel -xf realign.xf {0} {1}'.format(opts.modelIn,
            opts.modelOut)
        subprocess.call(cmd.split())
    
