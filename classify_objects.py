#!/usr/bin/env python

from __future__ import division

import subprocess
import pyimod
import numpy as np

def imodinfo_e(fname, obj, ncont):
    cmd = "imodinfo -e -o {0} {1}".format(obj + 1, fname)
    proc = subprocess.Popen(cmd.split(), stdout = subprocess.PIPE)
    M = np.zeros([ncont, 4])
    data_switch = 0 
    C = 1 
    for line in proc.stdout:
        if not data_switch and "semi-major" in line:
            data_switch = 1 
        elif data_switch and C <= ncont:
            line = line.split()
            M[C-1,0] = line[4]
            M[C-1,1] = line[5]
            M[C-1,2] = line[6]
            M[C-1,3] = line[7]
            C+=1   
    return M

def imodinfo_v(fname, obj, ncont):
    cmd = "imodinfo -v -o {0} {1}".format(obj + 1, fname)
    proc = subprocess.Popen(cmd.split(), stdout = subprocess.PIPE)
    M = np.zeros([ncont, 13])
    C = -1
    for line in proc.stdout:
        if "CONTOUR" in line:
            C+=1
            M[C,0] = line.split()[2] #N points
        elif "Closed/Open length" in line:
            M[C,1] = line.split()[3] #Closed length
            M[C,2] = line.split()[5] #Open length
        elif "Enclosed Area" in line:
            M[C,3] = line.split()[3] #Area
        elif "Center of Mass" in line:
            M[C,4] = line.split()[4][1:-1] #Centroid X
            M[C,5] = line.split()[5][0:-1] #Centroid Y
            M[C,6] = line.split()[6][0:-1] #Centroid Z
        elif "Circle" in line:
            M[C,7] = line.split()[2] #Circle
        elif "Orientation" in line:
            M[C,8] = line.split()[2] #Orientation
        elif "Ellipse" in line:
            M[C,9] = line.split()[2] #Ellipse
        elif "Length X Width" in line:
            M[C,10] = line.split()[4] #Length
            M[C,11] = line.split()[6] #Width
        elif "Aspect Ratio" in line:
            M[C,12] = line.split()[3] #Aspect Ratio
        elif "Total volume inside mesh" in line:
            volume = line.split()[5] #Volume
        elif "Total mesh surface area" in line:
            sa = line.split()[5] #Surface Area
    return M, volume, sa

if __name__ == '__main__':

    # Load model file
    fname = 'ZT04_01_isotropic_nuclei_L8_sort.mod'
    print "Loading IMOD model file: {0}".format(fname)
    mod = pyimod.ImodModel(fname)

    # Remove empty contours and objects with <=1 contours
    print "Removing empty contours and objects."
    mod.removeEmptyContours()
    mod.filterByNContours('>', 1)

    # Write output to a temporary model file
    fname_tmp = pyimod.utils.random_filename(30)
    print "Writing to temporary IMOD model file: {0}".format(fname_tmp)
    pyimod.ImodWrite(mod, fname_tmp)

    # Read temporary IMOD model file
    mod = pyimod.ImodModel(fname_tmp) 

    # Loop over all objects. Extract relevant features
    for i in range(0, mod.nObjects):
        M, vol, sa = imodinfo_v(fname_tmp, i, mod.Objects[i].nContours)
        print M

