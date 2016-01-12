from __future__ import division
import struct
from .ImodObject import ImodObject
from .ImodContour import ImodContour
from .utils import is_integer, is_string

class ImodModel(object):
    global unitDict, opsDict
    unitDict = {'pix': 0, 'km': 3, 'm': 1, 'cm': -2, 'mm': -3, 'microns': -6,
        'nm': -9, 'Angstroms': -10, 'pm': -12}

    opsDict = {'>': (lambda x,y: x>y),
          '<': (lambda x,y: x<y),
          '>=': (lambda x,y: x>=y),
          '<=': (lambda x,y: x<=y),
          '=': (lambda x,y: x==y),
          '==': (lambda x,y: x==y)}

    def __init__(self,
        filename = None,
        debug = 0,
        fid = 0,
        endianformat = "ieee-be",
        version = "V1.2",
        name = "ImodModel",
        xMax = 0,
        yMax = 0,
        zMax = 0,
        nObjects = 0,
        flags = 0,
        drawMode = 1,
        mouseMode = 0,
        blackLevel = 0,
        whiteLevel = 255,
        xOffset = 0,
        yOffset = 0,
        zOffset = 0,
        xScale = 0,
        yScale = 0,
        zScale = 0,
        object = 0,
        contour = 0,
        point = 0,
        res = 3,
        thresh = 0,
        pixelSizeXY = 1,
        pixelSizeZ = 1,
        units = 0,
        csum = 0,
        alpha = 0,
        beta = 0,
        gamma = 0,
        **kwargs):
            self.Objects = []
            self.__dict__.update(kwargs)
            self.__dict__.update(locals())
            if filename is None: 
                self.filename = ''
            else:
                self.filename = filename
                self.read_file()
            self.pixelSizeZ = self.zScale * self.pixelSizeXY
            self.setUnitsStr()

    def print_header(self):
        print "Filename: {0}".format(self.filename)
        print ""
        print "Image Dimensions: {0} {1} {2}".format(self.xMax, self.yMax, 
            self.zMax)
        print "Image Offsets: {0} {1} {2}".format(self.xOffset, self.yOffset,
            self.zOffset)
        print ""
        print "Number of Objects: {0}".format(self.nObjects)
        print "Model Scales: {0} {1} {2}".format(self.xScale, self.yScale,
            self.zScale)
        print "Voxel Size (X/Y): {0} {1}".format(self.pixelSizeXY, self.units)
        print "Voxel Size (Z): {0} {1}".format(self.pixelSize * self.zScale,
            self.units)

    def read_file(self):
        with open(self.filename, mode = "rb") as fid:
            self.fid = fid
            data = fid.read(8)
            if self.debug == 1:
                print data[0:4]
            self.version = data[4:9]
            data = fid.read(128)
            self.name = data.rstrip('\0')
            self.xMax = struct.unpack('>l', fid.read(4))[0]
            self.yMax = struct.unpack('>l', fid.read(4))[0]
            self.zMax = struct.unpack('>l', fid.read(4))[0]
            self.nObjects = struct.unpack('>l', fid.read(4))[0]
            self.flags = struct.unpack('>l', fid.read(4))[0]
            self.drawMode = struct.unpack('>l', fid.read(4))[0]
            self.mouseMode = struct.unpack('>l', fid.read(4))[0]
            self.blackLevel = struct.unpack('>l', fid.read(4))[0]
            self.whiteLevel = struct.unpack('>l', fid.read(4))[0]
            self.xOffset = struct.unpack('>f', fid.read(4))[0]
            self.yOffset = struct.unpack('>f', fid.read(4))[0]
            self.zOffset = struct.unpack('>f', fid.read(4))[0]
            self.xScale = struct.unpack('>f', fid.read(4))[0]
            self.yScale = struct.unpack('>f', fid.read(4))[0]
            self.zScale = struct.unpack('>f', fid.read(4))[0]
            self.object = struct.unpack('>l', fid.read(4))[0]
            self.contour = struct.unpack('>l', fid.read(4))[0]
            self.point = struct.unpack('>l', fid.read(4))[0]
            self.res = struct.unpack('>l', fid.read(4))[0]
            self.thresh = struct.unpack('>l', fid.read(4))[0]
            self.pixelSizeXY = struct.unpack('>f', fid.read(4))[0]
            self.units = struct.unpack('>l', fid.read(4))[0]
            self.csum = struct.unpack('>l', fid.read(4))[0]
            self.alpha = struct.unpack('>f', fid.read(4))[0]
            self.beta = struct.unpack('>f', fid.read(4))[0]
            self.gamma = struct.unpack('>f', fid.read(4))[0]

            if self.debug == 2:
                self.dump()

            iObject = 1
            while iObject <= self.nObjects:          
                data = fid.read(64)
                datatype = data[0:4]
                fid.seek(-64, 1)
                if self.debug == 1:
                    print datatype
                if datatype == 'OBJT':
                    self.Objects.append(ImodObject(self.fid,
                        debug = self.debug))
                    iObject = iObject + 1
                elif datatype == 'IEOF':
                    break
                elif datatype == 'VIEW':
                    break
        fid.close()
        return self

    def setAll(self, color = None, linewidth = None, transparency = None,
        name = None):
        """
        Changes object properties for all objects in a model file.
        """
        for iObject in range(0, self.nObjects): 
            if color:
                self.Objects[iObject].setColor(color)
            if linewidth:
                self.Objects[iObject].setLineWidth(linewidth)
            if transparency:
                self.Objects[iObject].setTransparency(transparency)
            if name:
                self.Objects[iObject].setName(name)
        return self

    def setUnitsStr(self):
        """
        Sets the unit string according to the integer value read from the file.
        """
        for unitStr, unitInt in unitDict.iteritems():
            if int(unitInt) == self.units:
                self.unitsStr = unitStr
                break
            else:
                self.unitsStr = 'Unknown'
        return self

    def setPixelSize(self, pixSize):
        """
        Changes the model's pixel size and updates its zScale accordingly
        """
        self.pixelSizeXY = float(pixSize)
        self.zScale = self.pixelSizeZ / self.pixelSizeXY
        return self

    def setUnits(self, units):
        """
        Changes the model's pixel string and updates its pixel integer ID 
        accordingly.
        """
        is_string(units, 'Units')
        self.unitsStr = units
        if unitDict.has_key(units):
            self.units = unitDict[units]
        else:
            self.units = 0
        return self

    def filterByNContours(self, compStr, nCont):
        """
        Removes all objects that do not satisfy the supplied conditional
        statement. The operator is specified by compStr, which may be: '>', 
        '<', '>=', '<=', or '='. The desired number of contours is specified by
        nCont. For example, (..., '>', 10) would keep only objects that have
        greater than 10 contours. 
        """
        is_string(compStr, 'Comparison string')
        is_integer(nCont, 'Number of contours')
        if not opsDict.has_key(compStr):
            raise ValueError('{0} is not a valid operator'.format(compStr))

        # Loop to check for nContours conditional statement
        c = 0
        ckeep = 0
        while c < self.nObjects:
            if not opsDict[compStr] (self.Objects[ckeep].nContours, nCont):
                del(self.Objects[ckeep]) 
            else:
                ckeep+=1
            c+=1

        # Update # of objects
        self.nObjects = len(self.Objects)
        return self

    def filterByMeshDistance(self, objRef, compStr, d_thresh, **kwargs):
        """
        Removes all objects that do not satisfy a distance criterion from a
        reference mesh. Euclidean distances are computed between the vertices
        of the reference object and all other objects in the model.
        
        Required
        ========
        objRef: Reference object, ranging from 1 - self.nObjects
        compStr: Comparison string in opsDict
        d_thresh: Distance threshold for removal, whose units are the same as
                  those specified in self.unitsStr

        Optional
        ========
        skip: Vertices to skip in each mesh (e.g. skip = 2 will skip every
              other vertex). This can be used to save time.
        """
        global np, cdist
        import numpy as np
        from scipy.spatial.distance import cdist

        skip = kwargs.get('skip', 1)

        is_integer(objRef, 'Reference Object')
        is_string(compStr, 'Comparison String')
        is_integer(d_thresh, 'Distance')

        if not opsDict.has_key(compStr):
            raise ValueError('{0} is not a valid operator'.format(compStr))
   
        if objRef > self.nObjects:
            raise valueError('Reference object does not exist within the model.')

        v_ref = get_vertices(self, objRef - 1, skip)

        c = 0 
        ckeep = 0 
        while c < self.nObjects:
            if c == objRef - 1:
                c+=1
                ckeep+=1
                continue
            v_test = get_vertices(self, ckeep, skip)
            d_min = calc_min_dist(v_ref, v_test)
            if not opsDict[compStr] (d_min, d_thresh):
                del(self.Objects[ckeep])
                decStr = 'REMOVED'
            else:
                ckeep+=1
                decStr = ''
            print "{0}. dmin = {1} {2}. {3}".format(str(c+1).zfill(6), d_min, self.unitsStr, decStr)
            c+=1

        self.nObjects = len(self.Objects)
        return self

    def filterByContourDistance(self, objRef, compStr, d_thresh, **kwargs):
        global np, cdist
        import numpy as np
        from scipy.spatial.distance import cdist 

        skip_ref = kwargs.get('skip_ref', 1)
        skip_cont = kwargs.get('skip_cont', 1)

        is_integer(objRef, 'Reference Object')
        is_string(compStr, 'Comparison String')
        is_integer(d_thresh, 'Distance')

        if not opsDict.has_key(compStr):
            raise ValueError('{0} is not a valid operator'.format(compStr))

        if objRef > self.nObjects:
            raise valueError('Reference object does not exist within the model.')

        v_ref = get_vertices(self, objRef - 1, skip_ref)

        iObject = 0
        while iObject < self.nObjects:
            if iObject == objRef - 1:
                iObject+=1
                continue
            c = 0
            ckeep = 0
            while c < self.Objects[iObject].nContours:
                pts_test = get_points(self, iObject, ckeep, skip_cont)
                d_min = calc_min_dist(v_ref, pts_test)
                if not opsDict[compStr] (d_min, d_thresh):
                    del(self.Objects[iObject].Contours[ckeep])
                    decStr = 'REMOVED'
                else:
                    ckeep+=1
                    decStr = ''
                print "{0} {1}. dmin = {2} {3}. {4}".format(str(iObject+1).zfill(6), str(c+1).zfill(6), d_min, self.unitsStr, decStr)
                c+=1
            self.Objects[iObject].nContours = len(self.Objects[iObject].Contours)
            iObject+=1
        return self      

    def removeEmptyContours(self):
        for iObject in range(0, self.nObjects):
            self.Objects[iObject].filterByNPoints('>', 0)
        return self

    def removeSmallContours(self):
        for iObject in range(0, self.nObjects):
            self.Objects[iObject].filterByNPoints('>', 2)
        return self

    def genSphereObject(self, center, r, N):
        import math
        pi = math.pi

        self.Objects.append(ImodObject())
        self.nObjects+=1

        zlst = range(-r+1, r)
        thetas = [(2*pi*i)/N for i in range(N)]

        for idx, z in enumerate(zlst):
            self.Objects[-1].Contours.append(ImodContour())
            phi = math.acos(z/r)
            pts = []
            for theta in thetas:
                x = r * math.sin(phi) * math.cos(theta) + center[0]
                y = r * math.sin(phi) * math.sin(theta) + center[1]
                pts.append(float("{0:0.2f}".format(x)))
                pts.append(float("{0:0.2f}".format(y)))
                pts.append(float(zlst[idx] + center[2]))
            self.Objects[-1].Contours[-1].points = pts
            self.Objects[-1].Contours[-1].nPoints = N
        self.Objects[-1].nContours = len(zlst)
        return self 

    def write(self, fname):
        with open(fname, mode = "wb") as fid:
            writeModelHeader(imodModel, fid)
            for iObject in range(0, imodModel.nObjects):
                writeObjectHeader(imodModel, iObject, fid)
                for iContour in range(0, imodModel.Objects[iObject].nContours):
                    writeContour(imodModel, iObject, iContour, fid)
                for iMesh in range(0, imodModel.Objects[iObject].nMeshes):
                    writeMesh(imodModel, iObject, iMesh, fid)
                writeIMAT(imodModel, iObject, fid)
                writeChunk(imodModel, iObject, fid)
            fid.write('IEOF')
            fid.close()


    def dump(self):
        from collections import OrderedDict as od
        for key, value in od(sorted(self.__dict__.items())).iteritems():
            print key, value
        print "\n"

"""
Utilities
"""

def get_vertices(model, iObject, skip):
    if len(model.Objects[iObject].Meshes) > 1:
        raise valueError('Object {0} has more than 1 mesh'.format(iObject))
    v = np.array(model.Objects[iObject].Meshes[0].vertices)
    v = v.reshape(v.shape[0]/3, 3)
    v = v[0::2]
    v = v[0::skip]
    v = np.array([model.pixelSizeXY, model.pixelSizeXY, model.pixelSizeZ] * v)
    return v

def get_points(model, iObject, iContour, skip):
    p = np.array(model.Objects[iObject].Contours[iContour].points)
    p = p.reshape(p.shape[0]/3, 3)
    p = p[0::skip]
    p = np.array([model.pixelSizeXY, model.pixelSizeXY, model.pixelSizeZ] * p)
    return p

def calc_min_dist(pts_ref, pts_test):
    d_min = float('Inf')
    for i in range(0, pts_test.shape[0] - 1):
        d = cdist(pts_ref, pts_test[[i, i+1]], 'euclidean')
        d = np.reshape(d, d.shape[0] * d.shape[1], 1)
        d_min_idx = np.argmin(d)
        d_min_i = d[d_min_idx]
        if d_min_i < d_min:
            d_min = d_min_i
    return d_min
