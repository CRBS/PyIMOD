#! /usr/bin/env python

from __future__ import division

import os
import numpy
from pyimod import utils, imodinfo
from scipy import stats
from optparse import OptionParser

# Parse input arguments
def parse_args():
    global p
    p = OptionParser(usage = "%prog [options] file_in.mrc file_in.mod")
    p.add_option("--verbose", action = "store_true", dest = "verbose",
                 help = "Prints additional output.")
    (opts, args) = p.parse_args()
    file_mrc, file_mod = check_args(args)
    return opts, file_mrc, file_mod

# Check validity of arguments
def check_args(args):
    if len(args) is not 2:
        usage("Improper number or arguments.")
    file_mrc = args[0]
    file_mod = args[1]
 
    # Check validity of MRC file 
    if not os.path.isfile(file_mrc):
        usage("{0} does not exist.".format(file_mrc))
    if utils.check_mrc(file_mrc):
        usage("{0} is not a valid mrc file.".format(file_mrc))

    # Check validity of IMOD model file
    if not os.path.isfile(file_mod):
        usage("{0} does not exist.".format(file_mod))

    return file_mrc, file_mod

# Print error messages and exit
def usage(errstr):
    print ""
    print "ERROR: {0}".format(errstr)
    print ""
    p.print_help()
    print ""
    exit(1)

# Calculate stats from integer/float list
def calculate_stats(list):
    stats_list = []
    stats_list.append(min(list)) #Min
    stats_list.append(max(list)) #Max
    stats_list.append(numpy.mean(list)) #Mean
    stats_list.append(numpy.std(list)) #Standard deviation
    stats_list.append(numpy.var(list)) #Variance
    #stats_list.append(stats.kurtosis(list)) #Kurtosis
    #stats_list.append(stats.skew(list)) #Skewness
    return stats_list

if __name__ == "__main__": 
    opts, file_mrc, file_mod = parse_args()

    nobj = int(imodinfo.get_n_objects(file_mod))
    if not nobj:
        usage("{0} has zero valid objects.".format(file_mod))
   
    # Get voxel sizes from the MRC file
    voxel_size = utils.get_mrc_header(file_mrc, "pixel")
    voxel_size = [x / 10 for x in voxel_size]
 
    features = numpy.empty([nobj, 26])
    for i in range(0, nobj):
        obj_i = i + 1
        print obj_i
        # Extract basic and advanced metrics for the current object
        ncont, vol, sa, cent, bb = imodinfo.get_obj_basic_metrics(file_mod,
            obj_i) 
        npoints, length, area = imodinfo.get_obj_advanced_metrics(file_mod,
            obj_i)

        # Calculate morphological parameters
        sa_vol_ratio = sa / vol
        sphericity = (numpy.pi**(1/3) * (6*vol)**(2/3))/sa
        compactness = sa**(3/2) / vol

        # Calculate stats from contour-based metrics
        stats_npoints = calculate_stats(npoints)
        print stats_npoints
        stats_length = calculate_stats(length)
        stats_area = calculate_stats(area)

        # Convert bounding box and centroid coordinates to nm
        bb = numpy.asarray(bb)
        cent = numpy.asarray(cent)
        voxel_size = numpy.asarray(voxel_size)
        n_slices = bb[5] - bb[2]
        cont_ratio = ncont / n_slices

        cent = numpy.multiply(cent, voxel_size)
        bb = numpy.multiply(bb, numpy.append(voxel_size, voxel_size))

        # Compute aspect ratios
        bb_size_x = bb[3] - bb[0]
        bb_size_y = bb[4] - bb[1]
        bb_size_z = bb[5] - bb[2]
        size_list = numpy.asarray([bb_size_x, bb_size_y, bb_size_z])
        size_list = numpy.sort(size_list)
        aspect_ratio_12 = size_list[0] / size_list[1]
        aspect_ratio_13 = size_list[0] / size_list[2]
        aspect_ratio_23 = size_list[1] / size_list[2]

        # Compute average distance from centroid to bounding box corners
        d_bb1 = numpy.linalg.norm(cent - bb[0:3])
        d_bb2 = numpy.linalg.norm(cent - bb[3:6])
        d_avg = (d_bb1 + d_bb2) / 2
       
        fv = numpy.asarray([ncont, vol, sa, sa_vol_ratio, sphericity,
            compactness, cont_ratio, aspect_ratio_12, aspect_ratio_13,
            aspect_ratio_23, d_avg])
        fv = numpy.append(fv, numpy.asarray(stats_npoints))
        fv = numpy.append(fv, numpy.asarray(stats_length))
        fv = numpy.append(fv, numpy.asarray(stats_area))

        features[i,] = fv

    numpy.savetxt("fv.csv", features, delimiter = ",", newline = "\n")
