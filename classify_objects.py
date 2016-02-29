#!/usr/bin/env python

from __future__ import division

import os
import subprocess
import pyimod
import timeit
import math
import glob

import numpy as np
import multiprocessing as mp

from sklearn.cluster import KMeans

def imodinfo_e(fname, iObj, ncont):
    cmd = "imodinfo -e -o {0} {1}".format(iObj + 1, fname)
    proc = subprocess.Popen(cmd.split(), stdout = subprocess.PIPE)
    M = np.zeros([ncont, 5])
    data_switch = 0 
    C = 1 
    for line in proc.stdout:
        if not data_switch and "semi-major" in line:
            data_switch = 1 
        elif data_switch and C <= ncont: 
            line = line.split()
            if str(line[0]) == 'Mean':
                delta = ncont - C + 1
                for i in range(delta):
                    M[C-1,:] = np.nan
                    C+=1
                continue
            if C != int(line[0]):
                delta = int(line[0]) - C
                for i in range(delta): 
                    M[C-1,:] = np.nan
                    C+=1
            if C <= ncont:
                M[C-1,0] = float(line[4])
                M[C-1,1] = float(line[5])
                M[C-1,2] = M[C-1,0] / M[C-1,1]
                M[C-1,3] = float(line[6])
                M[C-1,4] = float(line[7])
                C+=1
    return M

def imodinfo_v(fname, iObj, ncont):
    cmd = "imodinfo -v -o {0} {1}".format(iObj + 1, fname)
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
            volume = float(line.split()[5]) / (1000 ** 3) #Volume
        elif "Total mesh surface area" in line:
            sa = float(line.split()[5]) / (1000 ** 2) #Surface Area
    return M, volume, sa

def calc_delta_centroid(iObj, z, fv):
    # Analyzes the change in centroid position in (X, Y) across slices, and
    # returns statistics for the whole object. Statistics computed are the
    # maximum change in Euclidean distance between two slices, the mean # change across all slices, and the variance of change.  #
    # Inputs
    #    iObj - Object number.
    #    z    - List of z coordinate of every contour in the object.
    #    fv   - Feature vector to append metrics to.
    #
    # Returns
    #    fv - Feature vector with metrics appended.
    xc = []
    yc = []
    d = []
    for i in range(z[0], z[-1] + 1):
        idx = np.where(z == i)[0]
        pts = []
      
        # Get points of all contours at current Z value
        for j in idx:
            pts.extend(mod.Objects[iObj].Contours[j].points)
       
        # Compute centroid components for the current Z value. Append them to 
        # the x and y centroid coordinate lists, xc and yc, respectively.
        if pts:
            Npts = int(len(pts) / 3)
            xci = sum([x * mod.pixelSizeXY / 1000 for x in pts[0::3]]) / Npts
            yci = sum([y * mod.pixelSizeXY / 1000 for y in pts[1::3]]) / Npts
        xc.append(xci)
        yc.append(yci)       

        # Compute the Euclidean distance between the (X,Y) centroid coordinates
        # of successive slices. Append to the distance list, d. 
        if len(xc) > 1:
            d.append(math.sqrt((xc[-1] - xc[-2]) ** 2 + (yc[-1] - yc[-2]) ** 2))

    # Append the maximum distance, mean distance, and variance of distance to
    # the feature vector.
    fv.append(np.max(d))
    fv.append(np.mean(d))
    fv.append(np.var(d))
    return fv

def calc_centroid_3d(iObj, fv):
    # Calculates the 3D centroid of the input object, as well as relevant
    # metrics, such as the furthest distance from the centroid to the list of
    # contour points. Centroid is calculated as the mean centroid.
    #
    # Inputs
    #    iObj - Object number.
    #    fv   - Feature vector to append metrics to.
    #
    # Returns
    #    fv - Feature vector with metrics appended.

    # Get a list of all points in the object
    ncont = mod.Objects[iObj].nContours
    pts = []
    for iCont in range(ncont):
        pts.extend(mod.Objects[iObj].Contours[iCont].points)
    npts = int(len(pts) / 3)
    ptsx = [x * mod.pixelSizeXY / 1000 for x in pts[0::3]]
    ptsy = [y * mod.pixelSizeXY / 1000 for y in pts[1::3]]
    ptsz = [z * mod.pixelSizeZ / 1000 for z in pts[2::3]]

    # Compute the 3D centroid of the entire object
    xci = sum(ptsx) / npts
    yci = sum(ptsy) / npts
    zci = sum(ptsz) / npts

    # Compute the maximum distance
    d = []
    for iPt in range(npts):
        dx = (ptsx[iPt] - xci) ** 2
        dy = (ptsy[iPt] - yci) ** 2
        dz = (ptsz[iPt] - zci) ** 2
        d.append(math.sqrt(dx + dy + dz))

    # Compute the proportion of slices above and below the centroid slice
    idx1 = np.where(np.asarray(ptsz) > zci)[0]
    idx2 = np.where(np.asarray(ptsz) < zci)[0]
    nzabove = len(np.unique(np.asarray(ptsz)[idx1]))
    nzbelow = len(np.unique(np.asarray(ptsz)[idx2]))
    pzabove = nzabove / (nzabove + nzbelow + 1)
    pzbelow = nzbelow / (nzabove + nzbelow + 1)

    fv.append(np.max(d))
    fv.append(pzabove)
    fv.append(pzbelow)
    return fv

def get_z_values(iObj):
    ncont = mod.Objects[iObj].nContours
    z = np.zeros([ncont, 1])
    # Get a list of the Z value of each contour
    for i in range(ncont):
        z[i] = np.unique([int(x) for x in mod.Objects[iObj].Contours[i].points[2::3]])
    return z

def calc_stats(datain, iObj, z, fv):
    D = []
    for i in range(z[0], z[-1] + 1):
        idx = np.where(z == i)[0]
        if len(idx): 
            datai = datain[idx]
            datai = datai[~np.isnan(datai)] 
            if len(datai):
                D = np.append(D, np.mean(datai))
    if len(D):
        fv.append(np.min(D))
        fv.append(np.max(D))
        fv.append(np.mean(D))
        fv.append(np.var(D))
    else:
        [fv.append(x) for x in [0, 0, 0, 0]]
    return fv

def fit_quadratic(Araw, iObj, z, fv):
    ncont = mod.Objects[iObj].nContours

    # Loop from the minimum Z to the maximum Z. Sum up the areas enclosed by
    # all contours on the given Z value. Convert area to microns squared, and
    # append to an area list (A).
    A = []
    for i in range(z[0], z[-1] + 1):
        idx = np.where(z == i)[0]
        A = np.append(A, sum(Araw[idx]) / (1000 ** 2)) 

    # Fit a quadratic to the evolution of area across Z. Calculate the R-
    # squared value of this fit.
    x = range(len(A))  
    p = np.polyfit(x, A, 2)
    rsq = calc_rsq(p, x, A)

    # Append values to the object's feature vector and return.
    fv.append(p[2])
    fv.append(rsq)
    return fv   

def calc_rsq(p, x, y):
    v = np.polyval(p, x)
    ybar = np.mean(y)
    sstot = sum((y - ybar) ** 2)
    ssres = sum((y - v) ** 2)
    return 1 - ssres/sstot

def extract_features(iObj):
    print "Processing Object {0}".format(iObj)
    iiv, volume, sa = imodinfo_v(fname_tmp, iObj, mod.Objects[iObj].nContours)
    iie = imodinfo_e(fname_tmp, iObj, mod.Objects[iObj].nContours)

    # Add values to object's feature vector
    fvi = []
    fvi.append(volume)
    fvi.append(sa)

    # Compute metrics from surface area and volume
    sav_ratio = sa / volume
    sphericity = (math.pi ** (1/3) * (6 * volume) ** (2/3)) / sa
    fvi.append(sav_ratio)
    fvi.append(sphericity)

    # Get list of the Z coordinate of each contour
    z = get_z_values(iObj)

    # Get fit metrics for a quadratic to contour area 
    fvi = fit_quadratic(iiv[:,3], iObj, z, fvi)

    # Get fit metrics for a quadratic to closed length
    fvi = fit_quadratic(iiv[:,2], iObj, z, fvi)

    # Get contour centroid metrics 
    fvi = calc_delta_centroid(iObj, z, fvi)

    # Get the standard distance
    fvi = calc_centroid_3d(iObj, fvi)

    fvi = calc_stats(iiv[:,7], iObj, z, fvi)
    fvi = calc_stats(iiv[:,12], iObj, z, fvi)

    fvi = calc_stats(iie[:,2], iObj, z, fvi)
    fvi = calc_stats(iie[:,3], iObj, z, fvi)

    # Write output csv
    fnameout = 'obj_' + str(iObj).zfill(6) + '.csv'
    fid = open(fnameout, 'w')
    fid.write(','.join([str(x) for x in fvi]))
    fid.close()

def run_ef():
    pool = mp.Pool(processes = ncpu)
    pool.map(extract_features, range(mod.nObjects))
#    for i in range(mod.nObjects): #range(mod.nObjects):
#        vol = extract_features(i)

if __name__ == '__main__':
    global fname_tmp, mod, ncpu

    # Use 3/4 of the machine's processors
    ncpu = int(mp.cpu_count() * 0.75)

    # Load model file
    fname = 'ZT04_01_isotropic_nuclei_L8_sort.mod'
    print "Loading IMOD model file: {0}".format(fname)
    mod = pyimod.ImodModel(fname)
    
    # Remove empty contours.
    print "Removing empty contours and objects."
    mod.removeEmptyContours()

    # Keep objects with greater than 2 contours. First, run in remove =
    # False mode to create a visual representation of the filter.
    mod_tmp = mod
    mod_tmp.filterByNContours('>', 2, remove = False)
    pyimod.ImodWrite(mod_tmp, 'output_01_filterByNContours.mod') 
    del(mod_tmp)
    mod.filterByNContours('>', 2)

    # Remove objects touching the border
    print "Removing border objects."
    mod_tmp = mod
    mod_tmp.removeBorderObjects(remove = False)
    pyimod.ImodWrite(mod_tmp, 'output_02_removeBorderObjects.mod')
    del(mod_tmp)
    mod.removeBorderObjects()
    
    # Re-order all contours to go in ascending stack order
    for i in range(0, mod.nObjects):
        mod.Objects[i].sortContours()
    
    # Write output to a temporary model file
    fname_tmp = pyimod.utils.random_filename(30)
    print "Writing to temporary IMOD model file: {0}".format(fname_tmp)
    pyimod.ImodWrite(mod, fname_tmp)
    del mod

    # Read temporary IMOD model file
    mod = pyimod.ImodModel(fname_tmp) 

    # Loop over all objects. Extract relevant features. Store each object's 
    # feature vector to an individually numbered CSV file.
    print timeit.timeit('run_ef()', 'from __main__ import run_ef', number = 1)

    # Append all individually numbered CSVs to one file
    filenames = sorted(glob.glob('obj_*.csv'))
    with open('features.csv', 'w') as fid:
        for fname in filenames:
            print "Loading file {0}".format(fname)
            with open(fname) as infile:
                fid.write(infile.read())
                fid.write('\n')
            os.remove(fname)
    
    # Load features 
    fv = np.loadtxt('features.csv', dtype = 'float', delimiter = ',')

    # Run clustering
    print "Running k-means clustering with N = 2." 
    kmeans = KMeans(n_clusters = 2)
    c = kmeans.fit_predict(fv)
    idx = np.where(c)[0]
    print idx 

    # Manipulate objects according to clustering
    for iObj in range(mod.nObjects):
        if iObj in idx:
            mod.Objects[iObj].setColor(0, 1, 0)
        else:
            mod.Objects[iObj].setColor(1, 0, 0)

    # Write output model file
    print "Writing output IMOD file"
    pyimod.ImodWrite(mod, 'output_03_kmeans.mod')
