#!/usr/bin/env python

"""
Runs imodsortsurf to separate spatially disconnected objects into new objects,
and move all split objects to the end of the model file.

In the normal behavior of imodsortsurf, the original objects that new objects
are split from will remain in their original positions. This is not ideal if 
one wants to proofread only the split objects after running imodsortsurf.
"""

import sys 
import subprocess
from pyimod import *

fname = sys.argv[1]

# Load model
mod = ImodModel(fname)

# Remove empty objects (i.e. objects with zero contours)
mod.filterByNContours('>', 0)

# Remove meshes, re-mesh with a liberal cross-slice tolerance, and run
# imodsortsurf to separate objects.
nObjectsBefore = mod.nObjects
mod = ImodCmd(mod, 'imodmesh -e')
mod = ImodCmd(mod, 'imodmesh -CTs -P 10')
mod, stdout = ImodCmd(mod, 'imodsortsurf -s', return_output = True)
nObjectsAfter = mod.nObjects

# Parse the stored output of imodsortsurf to determine how many new objects
# were created from each input object.
objlist = []
for line in stdout:
    if 'Object' in line:
        line = line.split()
        objlist.append([int(line[1]), int(line[4])])

# Parse the object list, and find the objects that were actually split. Reverse
# the order of the list to facilitate proper removal.
objmove = []
for i in range(len(objlist)):
    if objlist[i][1] > 1:
        objmove.append(objlist[i][0]-1)
objmove = sorted(objmove, reverse = True)

# For each object that was split, append it to a new list of objects, then
# delete it from the open ImodModel object. This will leave the un-split
# objects as first in the object, followed by the newly split objects.
objects_to_append = []
for i in objmove:
    objects_to_append.append(mod.Objects[i])
    del(mod.Objects[i])

# Append the original objects that have now been split to the end of the file
mod.Objects.extend(objects_to_append)

# Append ImodView classes to each object to ensure proper writing
mod.view_objvsize = mod.nObjects
for iObject in range(mod.nObjects):
    if not mod.Objects[iObject].Views:
        mod.Objects[iObject].Views.append(ImodView.ImodView())
        r = mod.Objects[iObject].red
        g = mod.Objects[iObject].green
        b = mod.Objects[iObject].blue
        mod.Objects[iObject].Views[0].setColor(r, g, b)

# Remove meshes and save
mod = ImodCmd(mod, 'imodmesh -e')
ImodWrite(mod, fname + '_pyimodsortsurf') 
