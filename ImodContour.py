import struct

class ImodContour(object):

    def __init__(self,
        fid = None,
        nPoints = 0,
        flags = 0,
        type = 0,
        iSurface = 0,
        points = [],
        pointSizes = [],
        size_set = 0,
        **kwargs):
            self.__dict__.update(kwargs)
            self.__dict__.update(locals())
            self.size_vals = []
            if self.fid:
                self.read_file()    

    def read_file(self):
        fid = self.fid
        self.nPoints = struct.unpack('>l', fid.read(4))[0]
        self.flags = struct.unpack('>l', fid.read(4))[0]
        self.type = struct.unpack('>l', fid.read(4))[0]
        self.iSurface = struct.unpack('>l', fid.read(4))[0]
        self.points = struct.unpack('>{0}f'.format(3 * self.nPoints),
            fid.read(12 * self.nPoints))

        # Read the next data chunk. If it is SIZE, then set size_set to one and
        # read the values from the binary file. If not, seek back and continue.
        datatype = fid.read(4)
        if datatype == 'SIZE':
            self.size_set = 1
            psize = struct.unpack('>l', fid.read(4))[0]
            for i in range(0, psize, 4):
                self.size_vals.append(struct.unpack('>f', fid.read(4))[0])
        else:
            fid.seek(-4, 1)
        return self

    def dump(self):
        from collections import OrderedDict as od
        for key, value in od(sorted(self.__dict__.items())).iteritems():
            print key, value
        print "\n"

