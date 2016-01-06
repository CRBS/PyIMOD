import struct

class ImodMesh(object):

    def __init__(self,
        fid = None,
        debug = 0,
        nVertices = 0,
        nIndices = 0,
        flag = 0,
        type = 0,
        pad = 0,
        vertices = [],
        indices = [],
        **kwargs):
            self.__dict__.update(kwargs)
            self.__dict__.update(locals())
            if self.fid:
                self.read_file()    

    def read_file(self):
        fid = self.fid
        self.nVertices = struct.unpack('>l', fid.read(4))[0]
        self.nIndices = struct.unpack('>l', fid.read(4))[0]
        self.flag = struct.unpack('>l', fid.read(4))[0]
        self.type = struct.unpack('>h', fid.read(2))[0]
        self.pad = struct.unpack('>h', fid.read(2))[0] 
        self.vertices = struct.unpack('>{0}f'.format(3 * self.nVertices),
            fid.read(12 * self.nVertices))
        self.indices = struct.unpack('>{0}l'.format(self.nIndices),
            fid.read(4 * self.nIndices))
        return self

    def dump(self):
        print repr(self.__dict__)
