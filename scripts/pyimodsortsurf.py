#!/usr/bin/env python

import sys 
from pyimod import *

file = sys.argv[1]

# Load model
mod = ImodModel(file)

# Remove empty objects (i.e. objects with zero contours)
mod.filterByNContours('>', 0)

mod = ImodCmd('imodmesh -e')
mod = ImodCmd('imodmesh -CTs -P 10')
mod = ImodCmd('imodsortsurf -s')
