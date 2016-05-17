from __future__ import division

import os
import struct
import time
import cv2
import numpy as np
from .ImodObject import ImodObject
from .ImodContour import ImodContour
from .ImodWrite import ImodWrite
from .ImodView import ImodView
from .mrc import get_dims, mrc_to_numpy
from .utils import is_integer, is_string
from .features import *

class ImodModel(object):
    """
    Python class that reads and manipulates IMOD model files. IMOD is a set of
    image processing and modeling programs used principally by the microscopy
    community for generating 3D reconstructions (http://bio3d.colorado.edu/imod)

    The IMOD model file contains point, contour, object, and mesh data that can
    be overlaid on 3D image stacks and quantified. Model files are stored in the
    binary file format specified here: 

    http://bio3d.colorado.edu/imod/doc/binspec.html.

    The pyimod set of IMOD classes were created to give an automated way to 
    alter model properties such as color and name and to filter models by 
    certain criteria (i.e. number of contours, contour area, volume, sphericity,
    etc).

    ImodModel instances can be created in two different ways:

    1. By loading an existing IMOD model file:

    mod = pyimod.ImodModel('filename.mod')

    2. By creating an empty IMOD model file:

    mod = pyimod.ImodModel()

    The latter will create an empty model file with default settings and
    properties.
    """

    'Class used for reading and manipulating IMOD model files'

    # Declare dictionaries:
    #    1. unitDict: Correspondence between unit strings and the values they
    #       are stored as in the Imod binary model file.
    #    2. opsDict: Correspondence between inequality operators, input as 
    #       strings, and lambda functions that return the corresponding Boolean
    #       value, depending on whether the inequality is true. These are mostly
    #       used for filtering ImodModel instances based on object parameters.
    global unitDict, opsDict
    unitDict = {'pix': 0,
                'km': 3,
                'm': 1,
                'cm': -2,
                'mm': -3,
                'microns': -6,
                'nm': -9,
                'Angstroms': -10,
                'pm': -12}

    opsDict = {'>': (lambda x,y: x>y),
          '<': (lambda x,y: x<y),
          '>=': (lambda x,y: x>=y),
          '<=': (lambda x,y: x<=y),
          '=': (lambda x,y: x==y),
          '==': (lambda x,y: x==y)}

    def __init__(self,
        filename = None,
        cmap = {'name': 'imod'},
        debug = 0,
        fid = 0,
        endianformat = "ieee-be",
        version = "V1.2",
        name = "ImodModel",
        xMax = 0,
        yMax = 0,
        zMax = 0,
        nObjects = 0,
        flags = 15360,
        drawMode = 1,
        mouseMode = 2,
        blackLevel = 0,
        whiteLevel = 255,
        xOffset = 0,
        yOffset = 0,
        zOffset = 0,
        xScale = 1,
        yScale = 1,
        zScale = 1,
        object = 0,
        contour = 0,
        point = -1,
        res = 3,
        thresh = 0,
        pixelSizeXY = 1,
        pixelSizeZ = 1,
        units = 0,
        csum = 0,
        alpha = 0,
        beta = 0,
        gamma = 0,
        view_set = 0,
        view_4bytes = 0,
        view_fovy = 0,
        view_rad = 4190,
        view_aspect = 1,
        view_cnear = 0,
        view_cfar = 1,
        view_rot_x = -80,
        view_rot_y = -2,
        view_rot_z = -50,
        view_trans_x = -6262.07958984,
        view_trans_y = -4235.96142578,
        view_trans_z = -90.3249206543,
        view_scale_x = 1,
        view_scale_y = 1,
        view_scale_z = 1,
        view_mat = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
        view_world = 2,
        view_label = 'view 1',
        view_dcstart = 0,
        view_dcend = 1,
        view_lightx = 0,
        view_lighty = 0,
        view_plax = 5,
        view_objvsize = 0,
        minx_set = 0,
        minx_oscale = [0, 0, 0],
        minx_otrans = [0, 0, 0],
        minx_orot = [0, 0, 0],
        minx_cscale = [0, 0, 0],
        minx_ctrans = [0, 0, 0],
        minx_crot = [0, 0, 0], 
        **kwargs):
            self.Objects = []
            self.__dict__.update(kwargs)
            self.__dict__.update(locals())

            # If input filename is a string, attempt to read the model file. If
            # it is a pre-existing ImodModel object, read and store its
            # attributes to the new instance.
            if filename is None: 
                self.filename = ''
            elif type(filename).__name__ == 'str':
                self.filename = filename
                self.read_file()
            elif type(filename).__name__ == 'ImodModel':
                self.__dict__.update(filename.__dict__)
            self.pixelSizeZ = self.zScale * self.pixelSizeXY
            self.setUnitsStr()
            self.getColormap()

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
            self.name = data.split('\x00')[0]
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

            while True:
                data = fid.read(4)
                if self.debug == 1: 
                    print data
                if data == 'VIEW':
                    nViewBytes = struct.unpack('>i', fid.read(4))[0]
                    # Handle the case in which IMOD has created a 4 byte VIEW
                    # chunk, for some unknown reason
                    if nViewBytes == 4:
                        self.view_4bytes = 1
                        self.view_4bytes_cview = struct.unpack('>i', fid.read(4))[0]
                        continue
                    # Handle all other cases of the VIEW chunk
                    self.view_set = 1
                    self.read_view(fid)
                    for i in range(0, self.view_objvsize):
                        self.Objects[i].Views.append(ImodView(self.fid))
                elif data == 'MINX':
                    self.read_minx(fid)
                elif data == 'IEOF':
                    break
                else:
                    print data
                    break

        fid.close()
        return self

    def read_minx(self, fid):
        self.minx_set = 1
        fid.seek(4, 1)
        self.minx_oscale = [struct.unpack('>f', fid.read(4))[0] for x in [0, 1, 2]]
        self.minx_otrans = [struct.unpack('>f', fid.read(4))[0] for x in [0, 1, 2]]
        self.minx_orot = [struct.unpack('>f', fid.read(4))[0] for x in [0, 1, 2]]
        self.minx_cscale = [struct.unpack('>f', fid.read(4))[0] for x in [0, 1, 2]]
        self.minx_ctrans = [struct.unpack('>f', fid.read(4))[0] for x in [0, 1, 2]]
        self.minx_crot = [struct.unpack('>f', fid.read(4))[0] for x in [0, 1, 2]]        

    def read_view(self, fid):
        self.view_fovy = struct.unpack('>f', fid.read(4))[0]
        self.view_rad = struct.unpack('>f', fid.read(4))[0]
        self.view_aspect = struct.unpack('>f', fid.read(4))[0]
        self.view_cnear = struct.unpack('>f', fid.read(4))[0]
        self.view_cfar = struct.unpack('>f', fid.read(4))[0]
        self.view_rot_x = struct.unpack('>f', fid.read(4))[0]
        self.view_rot_y = struct.unpack('>f', fid.read(4))[0]
        self.view_rot_z = struct.unpack('>f', fid.read(4))[0]
        self.view_trans_x = struct.unpack('>f', fid.read(4))[0]
        self.view_trans_y = struct.unpack('>f', fid.read(4))[0]
        self.view_trans_z = struct.unpack('>f', fid.read(4))[0]
        self.view_scale_x = struct.unpack('>f', fid.read(4))[0]
        self.view_scale_y = struct.unpack('>f', fid.read(4))[0]
        self.view_scale_z = struct.unpack('>f', fid.read(4))[0]
        self.view_mat = []
        for i in range(0, 16):
            self.view_mat.append(struct.unpack('>f', fid.read(4))[0])
        self.view_world = struct.unpack('>i', fid.read(4))[0]
        data = fid.read(32)
        self.view_label = data.rstrip('\0')
        self.view_dcstart = struct.unpack('>f', fid.read(4))[0]
        self.view_dcend = struct.unpack('>f', fid.read(4))[0]
        self.view_lightx = struct.unpack('>f', fid.read(4))[0]
        self.view_lighty = struct.unpack('>f', fid.read(4))[0]
        self.view_plax = struct.unpack('>f', fid.read(4))[0]
        self.view_objvsize = struct.unpack('>i', fid.read(4))[0]
        fid.seek(4, 1)

    def addObject(self):
        self.Objects.append(ImodObject(cmap = self.cmap))
        self.nObjects+=1
        if self.view_set:
            self.Objects[-1].Views.append(ImodView())
            self.Objects[-1].Views[-1].red = self.Objects[-1].red
            self.Objects[-1].Views[-1].green = self.Objects[-1].green
            self.Objects[-1].Views[-1].blue = self.Objects[-1].blue
            self.view_objvsize+=1

    def removeAll(self, color = None, name = None):
        """
        Removes all objects that match a given property.
        """
        if color:
            is_string(color, 'RGB color string')
            rgb = [float(x) for x in color.split(',')]
            if len(rgb) != 3:
               raise ValueError('RGB string must have 3 values.')

        for iObject in range(self.nObjects - 1, -1, -1):
            if (color and rgb[0] == self.Objects[iObject].red and
               rgb[1] == self.Objects[iObject].green and
               rgb[2] == self.Objects[iObject].blue):
                del(self.Objects[iObject])
            if name and name == self.Objects[iObject].name:
                del(self.Objects[iObject])
     
        self.nObjects = len(self.Objects)
        if self.view_set:
            self.view_objvsize = self.nObjects

    def setAll(self, color = None, linewidth = None, transparency = None,
        name = None):
        """
        Changes object properties for all objects in a model file.
        """
        if color:
            is_string(color, 'RGB color string')
            rgb = [float(x) for x in color.split(',')]
            if len(rgb) != 3:
               raise ValueError('RGB string must have 3 values.')

        for iObject in range(self.nObjects): 
            if color:
                self.Objects[iObject].setColor(rgb[0], rgb[1], rgb[2])
            if linewidth:
                self.Objects[iObject].setLineWidth(linewidth)
            if transparency:
                self.Objects[iObject].setTransparency(transparency)
            if name:
                self.Objects[iObject].setName(name)

    def getColormap(self):
        file_cmap = os.path.join(os.path.dirname(__file__), 'colormaps',
            self.cmap['name'] + '.cmap')
        C = 0
        with open(file_cmap, 'r') as fid:
            for line in fid:
                self.cmap[str(C)] = line.split()
                C+=1
        fid.close()

    def getScale(self):
        scale = [1, 1, 1]
        if self.minx_set:
            scale = self.minx_cscale
        return scale

    def getTrans(self):
        trans = [0, 0, 0]
        if self.minx_set:
            trans = self.minx_ctrans
        return trans

    def setColormap(self, cmap):
        is_string(cmap, 'Colormap')
        file_cmap = os.path.join(os.path.dirname(__file__), 'colormaps',
            cmap + '.cmap')
        if not os.path.isfile(file_cmap):
            raise ValueError('The colormap file {0} does not exist.'.format(
                file_cmap))
        del(self.cmap)
        self.cmap = {'name': cmap}
        self.getColormap()

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

    def setPixelSizeXY(self, pixSize):
        """
        Changes the model's XY pixel size and updates its zScale accordingly
        """
        self.pixelSizeXY = float(pixSize)
        self.zScale = self.pixelSizeZ / self.pixelSizeXY

    def setPixelSizeZ(self, pixSize):
        """
        Changes the model's Z pixel size and updates its zScale accordingly
        """
        self.pixelSizeZ = float(pixSize)
        self.zScale = self.pixelSizeZ / self.pixelSizeXY

    def setImageSize(self, xMax, yMax, zMax):
        """
        Sets the maximum image dimensions (x, y, z) for the model. 
        """
        is_integer(xMax, 'xMax')
        is_integer(yMax, 'yMax')
        is_integer(zMax, 'zMax')
        if not all(x > 0 for x in [xMax, yMax, zMax]):
            raise ValueError('All dimension values must be > 0.')
        self.xMax = xMax
        self.yMax = yMax
        self.zMax = zMax 

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

    def filterByNContours(self, compStr, nCont, remove = True):
        """
        Removes all objects that do not satisfy the supplied conditional
        statement. The operator is specified by compStr, which may be: '>', 
        '<', '>=', '<=', or '='. The desired number of contours is specified by
        nCont. For example, (..., '>', 10) would keep only objects that have
        greater than 10 contours. 

        Inputs
        ======
        compStr - Comparison string, as described above.
        nCont   - Number of contours to filter by comparison with compStr.
        remove  - If True (default), will remove objects that do not meet the
                  comparison. If False, will keep all objects, but color those
                  that do not meet the comparison red, and those that do green.
        """
        is_string(compStr, 'Comparison string')
        is_integer(nCont, 'Number of contours')
        if not opsDict.has_key(compStr):
            raise ValueError('{0} is not a valid operator'.format(compStr))

        # Loop to check for nContours conditional statement
        for iObj in range(self.nObjects - 1, -1, -1):
            if not opsDict[compStr] (self.Objects[iObj].nContours, nCont):
                if remove:
                    del(self.Objects[iObj])
                else:
                    self.Objects[iObj].setColor(1, 0, 0)
            else:
                if not remove:
                    self.Objects[iObj].setColor(0, 1, 0)

        # Update # of objects and number of views, if these were changed.
        if remove:
            self.nObjects = len(self.Objects)
            if self.view_set:
                self.view_objvsize = len(self.Objects)

    def filterByNSlices(self, compStr, nSlices, remove = True):
        """
        Removes all objects that do not satisfy the supplied conditional 
        statement for the number of unique slices present.
        """ 
        is_string(compStr, 'Comparison string')
        is_integer(nSlices, 'Number of contours')
        if not opsDict.has_key(compStr):
            raise ValueError('{0} is not a valid operator'.format(compStr))
        
        for iObj in range(self.nObjects -1, -1, -1):
            zlist = self.Objects[iObj].get_z_values()
            nz = len(np.unique(np.asarray(zlist)))
            if not opsDict[compStr] (nz, nSlices):
                if remove:
                    del(self.Objects[iObj])
                else:
                    self.Objects[iObj].setColor(1, 0, 0)
            else:
                if not remove:
                    self.Objects[iObj].setColor(0, 1, 0)

        # Update # of objects and number of views, if these were changed.
        if remove:
            self.nObjects = len(self.Objects)
            if self.view_set:
                self.view_objvsize = len(self.Objects)

    def filterByContourArea(self, compStr, areaComp, remove = True):
        """
        Removes all objects taht do not satisfy the supplied conditional
        statement for the maximum area of a contour in the given object.
        """
        is_string(compStr, 'Comparison string')
        is_integer(areaComp, 'Maximum area')
        if not opsDict.has_key(compStr):
            raise ValueError('{0} is not a valid operator'.format(compStr))
    
        for iObj in range(self.nObjects -1, -1, -1):
            M, vol, sa = imodinfo_v(self.filename, iObj,
                self.Objects[iObj].nContours)
            amax = np.max(M[:, 3])
            print iObj+1, amax
            if not opsDict[compStr] (amax, areaComp):
                if remove:
                    del(self.Objects[iObj])
                else:
                    self.Objects[iObj].setColor(1, 0, 0)
            else:
                if not remove:
                    self.Objects[iObj].setColor(0, 1, 0)

        # Update # of objects and number of views, if these were changed.
        if remove:
            self.nObjects = len(self.Objects)
            if self.view_set:
                self.view_objvsize = len(self.Objects)

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
        if self.view_set:
            self.view_objvsize = self.nObjects

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

    def moveObjects(self, destObj, moveObjs):
        is_integer(destObj, 'Destination Object')
        destObj-=1
        if isinstance(moveObjs, (int, long)):
            objList = moveObjs
        else:
            objList = parse_obj_list(moveObjs)
        objList.sort()
        objList = list(reversed(objList))
        for i in objList:
            for j in range(0, len(self.Objects[i-1].Contours)):
                self.Objects[destObj].Contours.append(
                    self.Objects[i-1].Contours[j])
            #self.Objects[destObj].Contours.append(self.Objects[i-1].Contours)
            del(self.Objects[i-1])
        self.Objects[destObj].nContours = len(self.Objects[destObj].Contours)
        self.nObjects = len(self.Objects)

    def removeEmptyContours(self):
        for iObject in range(0, self.nObjects):
            self.Objects[iObject].filterByNPoints('>', 0)

    def removeSmallContours(self):
        for iObject in range(0, self.nObjects):
            self.Objects[iObject].filterByNPoints('>', 2)

    def genCubeObject(self, center, dim):
        self.addObject()

        if (dim % 2):
            zlst = range(-(dim//2), dim//2+1)
        else:
            zlst = range(-(dim//2)+1, dim//2+1)

        for z in zlst:
            self.Objects[-1].Contours.append(ImodContour())
            pts = []
            [pts.append(x) for x in [center[0] + dim/2, center[1] + dim/2,
                center[2] + z]]
            [pts.append(x) for x in [center[0] + dim/2, center[1] - dim/2,
                center[2] + z]]
            [pts.append(x) for x in [center[0] - dim/2, center[1] - dim/2,
                center[2] + z]]
            [pts.append(x) for x in [center[0] - dim/2, center[1] + dim/2,
                center[2] + z]]
            self.Objects[-1].Contours[-1].points = pts
            self.Objects[-1].Contours[-1].nPoints = 4
        self.Objects[-1].nContours = len(zlst)

    def genSphereObject(self, center, r, N):
        """
        Appends a new object to a model, and places a sphere with a specified
        center, radius, and number of points per contour in this new object.
        """
        import math
        pi = math.pi

        # Add ImodObject and ImodView objects
        self.addObject()

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

    def setFromTable(self, tname):
        file_table = os.path.join(os.path.dirname(__file__), 'tables',
            tname + '.csv')
        if not os.path.isfile(file_table):
            raise ValueError('The table file {0} does not exist.'.format(
                file_table))

        # Create table dictionary from the file
        td = {}
        C = 0
        with open(file_table) as f:
            for line in f:
                if not C:
                    if line[0] != '#' and not line[0].isspace():
                        line = line.rstrip('\n').split(',')
                        keys = [parse_name_str(x.replace("'", "")) for x in line]
                        C+=1
                    continue
                line = line.rstrip('\n').split(',')
                line = [x.replace("'", "") for x in line]
                td[line[0]] = line[1:]
        f.close()

        for iObject in range(self.nObjects):
            if keys[0] == 'name':
                iName = self.Objects[iObject].name
                if iName in td:
                    props = td[iName]
                    print "Editing object {0} named {1}.".format(iObject, iName)
                else:
                    continue
                for iProp in range(len(props)):
                    if keys[iProp+1] == 'color':
                        before = '{0:.2f},{1:.2f},{2:.2f}'.format(
                            self.Objects[iObject].red,
                            self.Objects[iObject].green,
                            self.Objects[iObject].blue)
                        r, g, b = [float(x) for x in props[iProp].split()]
                        self.Objects[iObject].setColor(r, g, b)
                        print "    Color: {0} --> {1:.2f},{2:.2f},{3:.2f}".format(
                            before, self.Objects[iObject].red, 
                            self.Objects[iObject].green, self.Objects[iObject].blue)
                    elif keys[iProp+1] == 'linewidth':
                        before = self.Objects[iObject].lineWidth2D
                        lw = int(props[iProp])
                        self.Objects[iObject].setLineWidth(lw)
                        print "    Line Width: {0} --> {1}".format(before, 
                            self.Objects[iObject].lineWidth2D)
                    elif keys[iProp+1] == 'transparency':
                        before = self.Objects[iObject].transparency
                        transp = int(props[iProp])
                        self.Objects[iObject].setTransparency(transp)
                        print "    Transparency: {0} --> {1}".format(before,
                            self.Objects[iObject].transparency)

    def removeBorderObjects(self, remove = True, fname = ''):
        """
        Removes all objects that contain contours touching either of the 6 
        bounds of the image stack. If the filename of an MRC file is supplied
        to the fname argument, a more rigorous search for boundary objects 
        will be performed such that objects that are touching alignment-
        induced borders will be removed. This on a slice-by-slice basis,
        sequentially over all slices as follows:
            1. Initialize a Numpy array of the current MRC slice.
            2. Compute the Sobel gradient magnitude of the image.
            3. Threshold the gradient magnitude, keeping only small values
               (e.g. values <= 1). These pixels are likely to correspond to
               borders, which have constant pixel value across the image.
            4. Compute the distance transform (DT) of the thresholded gradient
               magnitude.
            5. Loop over all objects in the model file. Find contours that are
               on the given slice. Test the value of DT at each point. If the
               value is very small (e.g. <= 3), assume the point is on or over
               the border and remove the object.

        Input
        =====
        remove  - If True (default), will remove objects that touch borders. If
                  False, will keep all objects, but color those that touch
                  borders red, and those that do not green.
        fname   - Filename of MRC for alignment-induced border removal.
        """
 
        # Loop over all objects and contours. Find objects containing contours
        # that touch either of the 6 borders. Append these object numbers to a
        # list, cdel for subsequent deletion.
        cdel = []
        for iObject in range(0, self.nObjects):
            for iContour in range(0, self.Objects[iObject].nContours):
                pts = self.Objects[iObject].Contours[iContour].points
                # Check if the contour's points contain any that touch either
                # of the 6 boundaries in x, y, or z. If so, append the object
                # number to the cdel list.
                if (sum([x < 1 for x in pts[0::3]]) or 
                    sum([x > self.xMax - 1 for x in pts [0::3]]) or
                    sum([y < 1 for y in pts[1::3]]) or
                    sum([y > self.yMax -1 for y in pts [1::3]]) or
                    (0 in pts[2::3]) or
                    (self.zMax - 1 in pts[2::3])):
                    cdel.append(iObject)
                    break

        # Loop over all objects, and remove those that are in cdel. If remove
        # is False, set the colors appropriately.
        for iObj in range(self.nObjects -1, -1, -1):
            if iObj in cdel:
                if remove:
                    del(self.Objects[iObj])
                else:
                    self.Objects[iObj].setColor(1, 0, 0)
            else:
                if not remove:
                    self.Objects[iObj].setColor(0, 1, 0)

        # Update the number of objects and views, if remove is True.
        if remove:
            self.nObjects -= len(cdel)
            if self.view_set:
                self.view_objvsize -= len(cdel)

        # Run alignment-induced border removal, if desired
        if fname:
            cdel = []
            nx, ny, nz = get_dims(fname)
            fid = open(fname, mode = "rb")
            fid.seek(1024, 0)
            for iSlice in range(nz):
                tic = time.clock()
                # Get slice from the MRC stack
                img = mrc_to_numpy(fid, nx, ny)

                # Get the distance transform
                dt = proc_border(img).astype('uint8')
                print np.max(dt)
                toc = time.clock()
               
                print "Slice {0} processed. Elapsed time: {1} seconds.".format(
                    iSlice + 1, toc - tic)

                for iObj in range(self.nObjects):
                    zvals = self.Objects[iObj].get_z_values()
                    idx = np.where(np.asarray(zvals) == iSlice + 1)[0]
                    if idx.any():
                        for iCont in idx:
                            pts = self.Objects[iObj].Contours[iCont].points
                            nPts = self.Objects[iObj].Contours[iCont].nPoints
                            pts = [int(x) for x in pts]
                            pts = np.reshape(pts, [nPts, 3])
                            pts[:,0] = pts[:,0] - 1
                            pts[:,1] = ny - pts[:,1] 
                            pts[:,[0, 1, 2]] = pts[:,[1, 0, 2]]
                            dtvals = np.asarray([dt[pts[x,0], pts[x,1]] for x in
                                range(nPts)])
                            idxdt = np.where(dtvals <= 3)[0]
                            if idxdt.any():
                                print "Remove Object {0}".format(iObj+1)
                                cdel.append(iObj)
            fid.close()

            # Loop over all objects, and remove those that are in cdel. If remove
            # is False, set the colors appropriately.
            for iObj in range(self.nObjects -1, -1, -1):
                if iObj in cdel:
                    if remove:
                        del(self.Objects[iObj])
                    else:
                        self.Objects[iObj].setColor(1, 0, 0)
                else:
                    if not remove:
                        self.Objects[iObj].setColor(0, 1, 0)

            # Update the number of objects and views, if remove is True.
            if remove:
                self.nObjects -= len(cdel)
                if self.view_set:
                    self.view_objvsize -= len(cdel)

    def mergeAll(self):
        """
        Merges all objects into Object #1
        """
        for iObj in range(self.nObjects-1, 0, -1):
            self.Objects[0].Contours = (self.Objects[0].Contours +
                self.Objects[iObj].Contours)
            self.Objects[0].nContours+=self.Objects[iObj].nContours
            del(self.Objects[iObj])
        self.nObjects = 1
        self.view_objvsize = 1

    def setAttributes(self, modin):
        for dictionary in modin:
            print dictionary    
 
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

def parse_obj_list(objs):
    objs = objs.split(',')
    lst = []
    for i in objs:
        splt = [int(x) for x in i.split('-')]
        if len(splt) == 1:
            lst.append(splt[0])
        else:
            [lst.append(x) for x in range(splt[0], splt[1]+1)]
    return lst

def parse_name_str(nstr):
    is_string(nstr, 'Name string')
    nstr = nstr.lower()
    d = {'name': 'name', 'names': 'name', 'object name': 'name',
        'object names': 'name', 'color': 'color', 'colors': 'color',
        'rgb': 'color', 'transparency': 'transparency', 'transp': 
        'transparency', 'line width': 'linewidth', 'linewidth':
        'linewidth'}

    if nstr in d:
        return d[nstr]
    else:
        raise ValueError('Invalid name string {0}'.format(nstr))

def proc_border(img):
    # Compute horizontal Sobel gradient
    sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0)
    sobelx = np.absolute(sobelx)

    # Compute vertical Sobel gradient
    sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1)
    sobely = np.absolute(sobely)

    # Compute gradient magnitude image
    mag = np.sqrt(sobelx ** 2 + sobely ** 2)  
    mag = np.uint8(mag)
    del(img, sobelx, sobely)

    # Threhold the gradient magnitude image
    mag = cv2.threshold(mag, 2, 1, cv2.THRESH_BINARY)[1]

    # Fill holes of the thresholded image
    contour, hier = cv2.findContours(mag, cv2.RETR_CCOMP,
        cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contour:
        cv2.drawContours(mag, [cnt], 0, 255, -1) 

    # Distance transform
    mag = cv2.distanceTransform(mag, cv2.cv.CV_DIST_L1,
        cv2.cv.CV_DIST_MASK_PRECISE)
    return mag
