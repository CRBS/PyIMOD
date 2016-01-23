#!/usr/bin/env python

import sys
from pyimod import *

file = sys.argv[1]

# Load model
mod = ImodModel(file)

# Remove empty objects (i.e. objects with zero contours)
mod.filterByNContours('>', 0)

# Remove all small contours, as these can cause problems with meshing and
# quantification in Amira.
mod.removeSmallContours()

# Set properties from the neuron_scn table
mod.setFromTable('neuron_scn')

# Mesh all objects
mod = ImodCmd(mod, 'imodmesh -CTs -P 4')

# Write file
ImodWrite(mod, file + '_out')
