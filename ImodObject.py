from __future__ import division

import struct
from .ImodContour import ImodContour
from .ImodMesh import ImodMesh
from .utils import is_integer, is_string

class ImodObject(object):

    def __init__(self,
        fid = None,
        debug = 0,
        name = '',
        nContours = 0,
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
        ambient = 0,
        diffuse = 0,
        specular = 0,
        shininess = 0,
        fillred = 0,
        fillgreen = 0,
        fillblue = 0,
        quality = 0,
        mat2 = 0,
        valblack = 0,
        valwhite = 0,
        matflags2 = 0,
        mat3b3 = 0,
        chunkID = 0,
        nChunkBytes = 0,
        **kwargs):
            self.Contours = []
            self.Meshes = []
            self.__dict__.update(kwargs)
            self.__dict__.update(locals())
            if self.fid:
                self.read_file()    

    def read_file(self):
        fid = self.fid
        data = fid.read(64)
        self.name = data[4:-1].rstrip('\0')
        fid.seek(68, 1)
        self.nContours = struct.unpack('>l', fid.read(4))[0]
        self.flags = struct.unpack('>l', fid.read(4))[0]
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

        datatype = fid.read(4)
        if self.debug == 1:
            print datatype
        if datatype == 'IMAT':
            self.read_imat(fid)

        # Read chunk data
        self.chunkID = struct.unpack('>i', fid.read(4))[0]
        self.nChunkBytes = struct.unpack('>l', fid.read(4))[0]
        fid.seek(self.nChunkBytes, 1)
        if self.debug == 1:
            print 'CHUNK', self.nChunkBytes

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

    def setColor(self, color):
        """
        Set object color by changing the red, green, and blue variables. The
        input color variable must be a string in the format 'R,G,B', where R,
        G, and B range either from 0-1 or 0-255.
        """
        is_string(color, 'Color')
        color = [float(x) for x in color.split(',')]
        if not ((0 <= color[0] <= 255) and (0 <= color[1] <= 255) and
            (0 <= color[2] <= 255)):
            raise ValueError('Color values must range from 0-1 or 0-255.')
        color = [x if x <= 1 else x/255 for x in color]
        self.red = color[0]
        self.green = color[1]
        self.blue = color[2]
        return self

    def setLineWidth(self, width):
        is_integer(width, 'Line Width')
        if not (1 <= width <= 10):
            raise ValueError('Line Width value must range from 1-10.')
        self.lineWidth2D = width
        return self

    def setTransparency(self, transp):
        is_integer(transp, 'Transparency')
        if not (0 <= transp <= 100):
            raise ValueError('Transparency value must range from 0-100.')
        self.transparency = transp
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

    def dump(self):
        from collections import OrderedDict as od
        for key, value in od(sorted(self.__dict__.items())).iteritems():
            print key, value
        print "\n"
