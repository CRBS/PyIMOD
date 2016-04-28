from __future__ import division

import os
import struct
import operator
import numpy as np
from itertools import count
from .ImodContour import ImodContour
from .ImodMesh import ImodMesh
from .utils import is_integer, is_string, set_bit, get_bit

class ImodObject(object):
    _ids = count(0)

    def __init__(self,
        fid = None,
        cmap = {'name': 'imod'},
        debug = 0,
        name = '',
        nContours = 0,
        objType = 'closed',
        flags = 0, 
        axis = 0,
        drawMode = 1,
        red = 0.0,
        green = 0.0,
        blue = 0.0,
        pdrawsize = 0.0,
        symbol = 1,
        symbolSize = 3,
        lineWidth2D = 1,
        lineWidth3D = 1,
        lineStyle = 0,
        symbolFlags = 0,
        sympad = 0,
        transparency = 0,
        nMeshes = 0,
        nSurfaces = 0,
        contour = '',
        mesh = '',
        surface = '',
        ambient = 102,
        diffuse = 255,
        specular = 127,
        shininess = 4,
        fillred = 0,
        fillgreen = 0,
        fillblue = 0,
        quality = 0,
        mat2 = 0,
        valblack = 0,
        valwhite = 255,
        matflags2 = 0,
        mat3b3 = 0,
        chunkID = 0,
        mepa_set = 0,
        mepa_nBytes = 0,
        **kwargs):
            self.id = self._ids.next()
            self.Contours = []
            self.Meshes = []
            self.Views = []
            self.mepa_byteString = []
            self.__dict__.update(kwargs)
            self.__dict__.update(locals())
            if self.fid:
                self.read_file()
            else:
                self.set_color_from_cmap()
            self.getObjectType()

    def read_file(self):
        fid = self.fid
        data = fid.read(64)
        self.name = data[4:-1].split('\x00')[0]
        fid.seek(68, 1)
        self.nContours = struct.unpack('>l', fid.read(4))[0]
        self.flags = struct.unpack('>I', fid.read(4))[0]
        self.axis = struct.unpack('>l', fid.read(4))[0]
        self.drawMode = struct.unpack('>l', fid.read(4))[0]
        self.red = struct.unpack('>f', fid.read(4))[0]
        self.green = struct.unpack('>f', fid.read(4))[0]
        self.blue = struct.unpack('>f', fid.read(4))[0]
        self.pdrawsize = struct.unpack('>l', fid.read(4))[0]
        self.symbol = struct.unpack('>B', fid.read(1))[0]
        self.symbolSize = struct.unpack('>B', fid.read(1))[0]
        self.lineWidth2D = struct.unpack('>B', fid.read(1))[0]
        self.lineWidth3D = struct.unpack('>B', fid.read(1))[0]
        self.lineStyle = struct.unpack('>B', fid.read(1))[0] 
        self.symbolFlags = struct.unpack('>B', fid.read(1))[0]
        self.sympad = struct.unpack('>B', fid.read(1))[0]
        self.transparency = struct.unpack('>B', fid.read(1))[0]
        self.nMeshes = struct.unpack('>l', fid.read(4))[0]
        self.nSurfaces = struct.unpack('>l', fid.read(4))[0]
 
        iContour = 1
        iMesh = 1
        while ( iContour <= self.nContours ) or ( iMesh <= self.nMeshes ):
            datatype = fid.read(4)
            if self.debug == 1:
                print datatype
            if datatype == 'CONT':
                self.Contours.append(ImodContour(fid, debug = self.debug))
                iContour = iContour + 1
            elif datatype == 'MESH':
                self.Meshes.append(ImodMesh(fid, debug = self.debug))
                iMesh = iMesh + 1

        while True:
            datatype = fid.read(4)
            if datatype == 'IMAT':
                if self.debug == 1:
                    print datatype
                self.read_imat(fid)
            elif datatype == 'MEPA':
                self.mepa_set = 1
                self.mepa_nBytes = struct.unpack('>i', fid.read(4))[0]
                for i in range(self.mepa_nBytes):
                    self.mepa_byteString.append(struct.unpack('>B', 
                        fid.read(1))[0])
                if self.debug == 1:
                    print datatype, self.mepa_nBytes
            else:
                fid.seek(-4, 1)
                break

        if self.debug == 2:
            self.dump()

        return self

    def read_imat(self, fid):
        fid.seek(4, 1)
        self.ambient = struct.unpack('>B', fid.read(1))[0]
        self.diffuse = struct.unpack('>B', fid.read(1))[0]
        self.specular = struct.unpack('>B', fid.read(1))[0]
        self.shininess = struct.unpack('>B', fid.read(1))[0]
        self.fillred = struct.unpack('>B', fid.read(1))[0]
        self.fillgreen = struct.unpack('>B', fid.read(1))[0]
        self.fillblue = struct.unpack('>B', fid.read(1))[0]
        self.quality = struct.unpack('>B', fid.read(1))[0]
        self.mat2 = struct.unpack('>l', fid.read(4))[0] 
        self.valblack = struct.unpack('>B', fid.read(1))[0]
        self.valwhite = struct.unpack('>B', fid.read(1))[0]
        self.matflags2 = struct.unpack('>B', fid.read(1))[0]
        self.mat3b3 = struct.unpack('>B', fid.read(1))[0]
        return self

    def addContour(self):
        self.Contours.append(ImodContour())
        self.nContours+=1

    def set_color_from_cmap(self):
        if len(self.cmap) == 1:
            rgb = [0, 1, 0]
        else:
            idx = self.id - ((self.id // (len(self.cmap) - 1)) * (len(self.cmap) - 1))
            rgb = self.cmap[str(idx)]
        self.setColor(rgb[0], rgb[1], rgb[2])

    def setColor(self, r, g, b):
        """
        Set object color by changing the red, green, and blue variables. The
        input color variable must be a string in the format 'R,G,B', where R,
        G, and B range either from 0-1 or 0-255.
        """
        color = [float(x) for x in [r, g, b]]
        if not all(0 <= x <= 255 for x in color):
            raise ValueError('Color values must range from 0-1 or 0-255.')

        color = [x if x <= 1 else x/255 for x in color]
        self.red = color[0]
        self.green = color[1]
        self.blue = color[2]
        for iView in range(len(self.Views)):
            self.Views[iView].setColor(color[0], color[1], color[2])

    def setFilledContoursOutlineOn(self):
        self.flags = set_bit(self.flags, 26, 1)
        return self

    def setFilledContoursOutlineOff(self):
        self.flags = set_bit(self.flags, 26, 0)
        return self

    def setLineWidth(self, width):
        is_integer(width, 'Line Width')
        if not (1 <= width <= 10):
            raise ValueError('Line Width value must range from 1-10.')
        self.lineWidth2D = width
        return self

    def setName(self, name):
        is_string(name, 'Name')
        if not (1 <= len(name) <= 64):
            raise ValueError('Name must be between 1-64 characters long.')
        self.name = name
        return self 

    def setObjectType(self, objType):
        is_string(objType, 'Object Type')
        if objType == 'scattered':
            self.flags = set_bit(self.flags, 9, 1)
            self.flags = set_bit(self.flags, 3, 1)
        elif objType == 'open':
            self.flags = set_bit(self.flags, 9, 0)
            self.flags = set_bit(self.flags, 3, 1)
        elif objType == 'closed':
            self.flags = set_bit(self.flags, 9, 0)
            self.flags = set_bit(self.flags, 3, 0)
        else:
            raise ValueError('Invalid object type {0}.'.format(objType))

        # Update the ImodView flags
        if self.Views:
            self.Views[0].flags = self.flags
        self.getObjectType()

    def getObjectType(self):
        bit9 = get_bit(self.flags, 9)
        bit3 = get_bit(self.flags, 3)
        if bit3 and bit9:
            self.objType = 'scattered'
        if bit3 and not bit9:
            self.objType = 'open'

    def setMeshOn(self):
        self.flags = set_bit(self.flags, 8, 1)
        self.flags = set_bit(self.flags, 10, 1)
        if self.Views:
            self.Views[0].flags = self.flags        

    def setTransparency(self, transp):
        is_integer(transp, 'Transparency')
        if not (0 <= transp <= 100):
            raise ValueError('Transparency value must range from 0-100.')
        self.transparency = transp
        for iView in range(len(self.Views)):
            self.Views[iView].setTransparency(transp)
        return self

    def setSymbolType(self, symbolStr):
        is_string(symbolStr, 'Symbol String')
        symbDict = {'circle': 0, 'none': 1, 'square': 2, 'triangle': 3, 
            'star':4}
        if not symbDict.has_key(symbolStr):
            raise ValueError('{0} is not a valid symbol type'.format(symbolStr))
        self.symbol = symbDict[symbolStr]
        return self

    def setSymbolSize(self, symbolSize):
        is_integer(symbolSize, 'Symbol Size')
        if not (1 <= symbolSize <= 100):
            raise ValueError('Symbol size must be an integer between 1-100')
        self.symbolSize = symbolSize
        return self

    def setSymbolFillOn(self):
        self.symbolFlags = set_bit(self.symbolFlags, 0, 1)
        return self

    def setSymbolFillOff(self):
        self.symbolFlags = set_bit(self.symbolFlags, 0, 0)
        return self 

    def filterByNPoints(self, compStr, nPoints):
        is_string(compStr, 'Comparison string')
        is_integer(nPoints, 'Number of points')
        ops = {'>': (lambda x,y: x>y), 
              '<': (lambda x,y: x<y),
              '>=': (lambda x,y: x>=y), 
              '<=': (lambda x,y: x<=y),
              '=': (lambda x,y: x==y),
              '==': (lambda x,y: x==y)}
        if not ops.has_key(compStr):
            raise ValueError('{0} is not a valid operator'.format(compStr))

        # Loop to check for nPoints conditional statement
        c = 0 
        ckeep = 0 
        while c < self.nContours:
            if not ops[compStr] (self.Contours[ckeep].nPoints, nPoints):
                del(self.Contours[ckeep]) 
            else:
                ckeep+=1
            c+=1

        # Update # of objects
        self.nContours = len(self.Contours)
        return self

    def sortContours(self):
        # Determine the Z value of each contour.
        zunique = [] 
        for i in range(0, self.nContours):
            zcoords_i = [round(x) for x in self.Contours[i].points[2::3]]
            zunique_i = list(set(zcoords_i))
            if len(zunique_i) > 1:
                return self
            else:
                zunique_i = zunique_i[0] 
            zunique.append(zunique_i)
        # Sort the unique Z values of the object. 
        zsort = sorted(enumerate(zunique), key = operator.itemgetter(1)) 

        # Re-order the contours accordingly
        contours_new = []
        for i in range(0, len(zsort)):
            contours_new.append(self.Contours[zsort[i][0]])
        self.Contours = contours_new

    def get_z_values(self):
        """
        Returns the z value of every contour in the object, ordered by contour
        index.

        Returns
        =======
        z - A (1 x ncont) list containing the unique z value of each contour.
        """
        z = []
        for iCont in range(self.nContours):
            z.append(np.unique([int(x) for x in 
                self.Contours[iCont].points[2::3]]).tolist()[0])
        return z

    def hasMissingSlices(self):
        """ 
        Returns True if the object has contours on all slices ranging from Zmin
        to Zmax. Otherwise, returns False.
        """
        zvals = self.get_z_values()
        zvals_unique = sorted(np.unique(zvals))
        zmin = zvals_unique[0]
        zmax = zvals_unique[-1]
        comp = np.asarray(range(zmin, zmax+1))
        return np.array_equal(zvals_unique, comp):

    def dump(self):
        from collections import OrderedDict as od
        for key, value in od(sorted(self.__dict__.items())).iteritems():
            print key, value
        print "\n"
