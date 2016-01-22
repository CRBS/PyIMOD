#!/usr/bin/env python

import sys
from pyimod import *

file = sys.argv[1]

mod = ImodModel(file)
mod.setFromTable('neuron_scn')
mod = ImodCmd(mod, 'imodmesh -CTs -P 4')

ImodWrite(mod, file + '_out')
