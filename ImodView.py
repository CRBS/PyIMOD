import struct

class ImodView(object):

    def __init__(self,
        fid = None,
        flags = 0,
        red = 0,
        green = 0,
        blue = 0,
        pdrawsize = 0,
        linewidth = 1,
        linesty = 0,
        trans = 0,
        clips_count = 0,
        clips_flags = 0,
        clips_trans = 0,
        clips_plane = 0,
        clips_normal_x = 0,
        clips_normal_y = 0,
        clips_normal_z = -1,
        clips_points_x = 0,
        clips_points_y = 0,
        clips_points_z = 0,
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
        mat3b2 = 0,
        mat3b3 = 0,
        clips_normal = [0, 0, -1] * 5,
        clips_point = [0] * 15,
        **kwargs):
            self.__dict__.update(kwargs)
            self.__dict__.update(locals())
            if self.fid:
                self.read_file()    

    def read_file(self):
        fid = self.fid
        self.flags = struct.unpack('>I', fid.read(4))[0]
        self.red = struct.unpack('>f', fid.read(4))[0]
        self.green = struct.unpack('>f', fid.read(4))[0]
        self.blue = struct.unpack('>f', fid.read(4))[0]
        self.pdrawsize = struct.unpack('>i', fid.read(4))[0]
        self.linewidth = struct.unpack('>B', fid.read(1))[0]
        self.linesty = struct.unpack('>B', fid.read(1))[0]
        self.trans = struct.unpack('>B', fid.read(1))[0]
        self.clips_count = struct.unpack('>B', fid.read(1))[0]
        self.clips_flags = struct.unpack('>B', fid.read(1))[0]
        self.clips_trans = struct.unpack('>B', fid.read(1))[0]
        self.clips_plane = struct.unpack('>B', fid.read(1))[0]
        self.clips_normal_x = struct.unpack('>f', fid.read(4))[0]
        self.clips_normal_y = struct.unpack('>f', fid.read(4))[0]
        self.clips_normal_z = struct.unpack('>f', fid.read(4))[0]
        self.clips_points_x = struct.unpack('>f', fid.read(4))[0]
        self.clips_points_y = struct.unpack('>f', fid.read(4))[0]
        self.clips_points_z = struct.unpack('>f', fid.read(4))[0]
        self.ambient = struct.unpack('>B', fid.read(1))[0]
        self.diffuse = struct.unpack('>B', fid.read(1))[0]
        self.specular = struct.unpack('>B', fid.read(1))[0]
        self.shininess = struct.unpack('>B', fid.read(1))[0]
        self.fillred = struct.unpack('>B', fid.read(1))[0]
        self.fillgreen = struct.unpack('>B', fid.read(1))[0]
        self.fillblue = struct.unpack('>B', fid.read(1))[0]
        self.quality = struct.unpack('>B', fid.read(1))[0] 
        self.mat2 = struct.unpack('>I', fid.read(4))[0]
        self.valblack = struct.unpack('>B', fid.read(1))[0]
        self.valwhite = struct.unpack('>B', fid.read(1))[0]
        self.mat3b2 = struct.unpack('>B', fid.read(1))[0]
        self.mat3b3 = struct.unpack('>B', fid.read(1))[0]
        self.clips_normal = []
        for i in range(0, 15):
            self.clips_normal.append(struct.unpack('>f', fid.read(4))[0])
        self.clips_point = []
        for i in range(0, 15):
            self.clips_point.append(struct.unpack('>f', fid.read(4))[0])
        return self

    def dump(self):
        from collections import OrderedDict as od
        for key, value in od(sorted(self.__dict__.items())).iteritems():
            print key, value
        print "\n"
