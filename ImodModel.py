import struct
from .ImodObject import ImodObject

class ImodModel(object):

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
            self.setUnitStr()

    def print_header(self):
        print "Filename: {0}".format(self.filename)
        print ""
        print "Image Dimensions: {0} {1} {2}".format(self.xMax, self.yMax, self.zMax)
        print "Image Offsets: {0} {1} {2}".format(self.xOffset, self.yOffset, self.zOffset)
        print ""
        print "Number of Objects: {0}".format(self.nObjects)
        print "Model Scales: {0} {1} {2}".format(self.xScale, self.yScale, self.zScale)
        print "Voxel Size (X/Y): {0} {1}".format(self.pixelSizeXY, self.units)
        print "Voxel Size (Z): {0} {1}".format(self.pixelSize * self.zScale, self.units)

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
                    self.Objects.append(ImodObject(self.fid, debug = self.debug))
                    iObject = iObject + 1
                elif datatype == 'IEOF':
                    break
                elif datatype == 'VIEW':
                    break
        fid.close()
        return self

    def setUnitStr(self):
        """
        Sets the unit string according to the integer value read from the file.
        """
        if self.units == 0:
            self.unitStr = "pix"
        elif self.units == 3:
            self.unitStr = "km"
        elif self.units == 1:
            self.unitStr = "m"
        elif self.units == -2:
            self.unitStr = "cm"
        elif self.units == -3:
            self.unitStr = "mm"
        elif self.units == -6:
            self.unitStr = "microns"
        elif self.units == -9:
            self.unitStr = "nm"
        elif self.units == -10:
            self.unitStr = "Angstroms"
        elif self.units == -12:
            self.unitStr = "pm"
        else:
            self.unitStr = "Unknown"
        return self

    def setPixelSize(self, pixSize):
        """
        Changes the model's pixel size and updaates its zScale accordingly
        """
        self.pixelSizeXY = float(pixSize)
        self.zScale = self.pixelSizeZ / self.pixelSizeXY
        return self

    def setUnits(self, units):
        """
        Changes the model's pixel string and updates its pixel integer ID 
        accordingly.
        """
        self.unitStr = units
        if self.unitStr == "pix":
            self.units = 0
        elif self.unitStr == "km":
            self.units = 3
        elif self.unitStr == "m":
            self.units = 1
        elif self.unitStr == "cm":
            self.units = -2
        elif self.unitStr == "mm":
            self.units = -3
        elif self.unitStr == "microns":
            self.units = -6
        elif self.unitStr == "nm"
            self.units = -9
        elif self.unitStr == "Angstroms":
            self.units = -10
        elif self.unitStr = "pm":
            self.units = -12
        else
            self.units = 0
        return self

    def dump(self):
        from collections import OrderedDict as od
        for key, value in od(sorted(self.__dict__.items())).iteritems():
            print key, value
        print "\n"