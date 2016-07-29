#!/usr/bin/env python

from __future__ import division

import os
import sys
import subprocess
from optparse import OptionParser
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
from pyimod import *

def parse_args():
    global p
    p = OptionParser(usage = "%prog [options] file.mod")
    p.add_option("--output",
                 dest = "path_out",
                 metavar = "PATH",
                 default = os.getcwd(),
                 help = "Path to write output files to. By default, files will "
                        "be written to the current working directory.")
    p.add_option("--objects",
                 dest = "objnumbers",
                 metavar = "STRING",
                 help = "Object numbers in the model file to convert to Amira. "
                        "Multiple numbers can be entered using IMOD syntax "
                        "(i.e. how newstack allows lists of sections using "
                        "commas and dashes). If multiple objects are being "
                        "used, the list of object numbers must be enclosed by "
                        "single quotes, e.g. --objects '1,2,5-10'")
    p.add_option("--launch_amira",
                 dest = "launch_amira",
                 action = "store_true",
                 default = False,
                 help = "Launches Amira automatically after conversion. Runs "
                        "the Amira binary specified by --amira_path.")
    p.add_option("--amira_path",
                 dest = "path_amira",
                 metavar = "PATH",
                 default = '/usr/local/apps/Amira/6.0.0/bin/Amira',
                 help = "Path to Amira binary. The default is the path at "
                        "NCMIR: /usr/local/apps/Amira/6.0.0/bin/Amira. ")
    (opts, args) = p.parse_args()
    file_in = check_args(args)
    return opts, file_in 

def check_args(args):
    if len(args) is not 1:
        usage("Improper number of arguments.")
    file_in = args[0]
    if not os.path.isfile(file_in):
        usage("{0} does not exist".format(fileModel))
    return file_in

def usage(errstr):
    print ""
    print "ERROR: {0}".format(errstr)
    print ""
    p.print_help()
    print ""
    exit(1)

def write_tcl_load_vrml(fid, vrml_in, iobj, rgb, transp):
    fid.write("set base [file tail {}]\n".format(vrml_in))
    fid.write("set base [string trimright $base \".wrl\"]\n")
    fid.write("[load {}] setLabel $base\n".format(vrml_in))
    fid.write("set module \"Scene-To-Surface-{}\"\n".format(iobj))
    fid.write("create HxGeometryToSurface $module\n")
    fid.write("$module data connect $base\n")
    fid.write("$module action snap\n")
    fid.write("$module fire\n")
    fid.write("set surf \"Geometry-Surface-{}\"\n".format(iobj))
    fid.write("\"GeometrySurface\" setLabel $surf\n")
    fid.write("set module \"Surface-View-{}\"\n".format(iobj))
    fid.write("create HxDisplaySurface $module\n")
    fid.write("$module data connect $surf\n")
    if transp:
        fid.write("$module drawStyle setValue 4\n") 
        fid.write("$module baseTrans setValue {}\n".format(transp))
    else:
        fid.write("$module drawStyle setValue 1\n")
    fid.write("$module drawStyle setNormalBinding 1\n")
    fid.write("$module colorMode setValue 5\n")
    fid.write("$module colormap setDefaultColor {0} {1} {2}\n".format(rgb[0],
        rgb[1], rgb[2]))
    fid.write("$module fire\n")
    fid.write("\n")

if __name__ == '__main__':
    opts, file_in = parse_args()

    # Check validity of output path. Make output directory if necessary.
    path_base, path_save = os.path.split(opts.path_out)
    if not path_base:
        path_base = '.'
    if not os.path.isdir(path_base):
        usage("The path {} does not exist.".format(path_base))
    if not os.path.isdir(opts.path_out):
        os.makedirs(opts.path_out)

    # Load input model file
    print "imod2amira"
    print "Loading {}...".format(file_in)
    modin = ImodModel(file_in)

    # Get the objects to convert. If a list is entered using the --objects flag,
    # parse this list and check for validity against the object numbers actually
    # contained in the model file. If the --objects flag is not used, convert 
    # all objects.
    objrange = range(modin.nObjects)
    if opts.objnumbers: 
        opts.objnumbers = [int(x) - 1 for x in parse_obj_list(opts.objnumbers)]
        for x in opts.objnumbers:
            if x not in objrange:
                usage("Invalid object numbers in --objects.")
    else:
        opts.objnumbers = objrange

    print "\n==========\n"

    # Open Amira TCL script to write to 
    file_tcl = os.path.abspath(os.path.join(opts.path_out, 
        file_in.split('.')[0] + ".hx"))
    fid = open(file_tcl, 'a+')

    # Loop over objects
    for iobj in opts.objnumbers:
        
        # Get pertinent object properties
        iobj_type = modin.Objects[iobj].objType
        iobj_nmeshes = modin.Objects[iobj].nMeshes
        iobj_name = modin.Objects[iobj].name
        iobj_rgb = []
        iobj_rgb.append(modin.Objects[iobj].red)
        iobj_rgb.append(modin.Objects[iobj].green)
        iobj_rgb.append(modin.Objects[iobj].blue)
        iobj_transp = float(modin.Objects[iobj].transparency) / 100
        print "Processing object {}".format(iobj+1)
        print "Object name: {}".format(iobj_name)
        print "Object color: {0}, {1}, {2}".format(iobj_rgb[0], iobj_rgb[1],
            iobj_rgb[2])
        print "Object transparency: {}".format(iobj_transp)
        print "Number of meshes: {}".format(iobj_nmeshes)

        # Check that meshes exist for the given object. If not, print warning
        # and skip.
        if not iobj_nmeshes and iobj_type is not 'scattered':
            print ("WARNING: Object {} does not contain any mesh data. "
                  "Skipping.\n\n==========\n".format(iobj+1))
            continue

        # Construct output VRML filename for the current object
        fname_str = "obj_" + str(iobj+1).zfill(len(str(modin.nObjects)))
        if len(iobj_name):
            fname_str += ("_" + "_".join(iobj_name.split()))
        fname_str += ".wrl"
        fname_out = os.path.abspath(os.path.join(opts.path_out, fname_str))
        print "Output file name: {}".format(fname_out) 

        # Convert to VRML
        if not iobj:
            ImodExport(modin, fname_out, object = iobj)
        else:
            ImodExport(modin, fname_out, object = iobj + 1)

        print "SUCCESS!\n\n==========\n"

        write_tcl_load_vrml(fid, fname_out, iobj + 1, iobj_rgb, iobj_transp)

    fid.close()

    # Launch Amira
    if opts.launch_amira:
        cmd = "{0} {1}".format(opts.path_amira, file_tcl)
        subprocess.call(cmd.split())
