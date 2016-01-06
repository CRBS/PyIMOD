import struct

def ImodWrite(imodModel, fname):
    with open(fname, mode = "wb") as fid:
        writeModelHeader(imodModel, fid)
        for iObject in range(0, imodModel.nObjects):
            writeObjectHeader(imodModel, iObject, fid)
        fid.close()
    
def writeModelHeader(imodModel, fid):
    tag = 'IMOD' + imodModel.version
    nChar = len(imodModel.name)
    nameStr = imodModel.name + '\0' * (128 - nChar)
    fid.write(tag)
    fid.write(nameStr)
    fid.write(struct.pack('>i', imodModel.xMax))
    fid.write(struct.pack('>i', imodModel.yMax))
    fid.write(struct.pack('>i', imodModel.zMax))
    fid.write(struct.pack('>i', imodModel.nObjects))
    fid.write(struct.pack('>I', imodModel.flags))
    fid.write(struct.pack('>i', imodModel.drawMode))
    fid.write(struct.pack('>i', imodModel.mouseMode))
    fid.write(struct.pack('>i', imodModel.blackLevel))
    fid.write(struct.pack('>i', imodModel.whiteLevel))
    fid.write(struct.pack('>f', imodModel.xOffset))
    fid.write(struct.pack('>f', imodModel.yOffset))
    fid.write(struct.pack('>f', imodModel.zOffset))
    fid.write(struct.pack('>f', imodModel.xScale))
    fid.write(struct.pack('>f', imodModel.yScale))
    fid.write(struct.pack('>f', imodModel.zScale))
    fid.write(struct.pack('>i', imodModel.object))
    fid.write(struct.pack('>i', imodModel.contour))
    fid.write(struct.pack('>i', imodModel.point))
    fid.write(struct.pack('>i', imodModel.res))
    fid.write(struct.pack('>i', imodModel.thresh))
    fid.write(struct.pack('>f', imodModel.pixelSize))
    fid.write(struct.pack('>i', imodModel.units))
    fid.write(struct.pack('>i', imodModel.csum))
    fid.write(struct.pack('>f', imodModel.alpha))
    fid.write(struct.pack('>f', imodModel.beta))
    fid.write(struct.pack('>f', imodModel.gamma))

def writeObjectHeader(imodModel, iObject, fid):
    tag = 'OBJT' + imodModel.Objects[iObject].name
    nchar = len(tag)
    tagStr = tag + '\0' * (128 - nChar)
    fid.write(tagStr)
    fid.write(struct.pack('>i', imodModel.Objects[iObject].nContours))
    fid.write(struct.pack('>I', imodModel.Objects[iObject].flags))
    fid.write(struct.pack('>i', imodModel.Objects[iObject].axis))
    fid.write(struct.pack('>i', imodModel.Objects[iObject].drawMode))
    fid.write(struct.pack('>f', imodModel.Objects[iObject].red))
    fid.write(struct.pack('>f', imodModel.Objects[iObject].green))
    fid.write(struct.pack('>f', imodModel.Objects[iObject].blue))
    fid.write(struct.pack('>i', imodModel.Objects[iObject].pdrawsize))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].symbol))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].symbolSize))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].lineWidth2D))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].lineWidth3D))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].lineStyle))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].symbolFlags))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].sympad))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].transparency))
    fid.write(struct.pack('>i', imodModel.Objects[iObject].nMeshes))
    fid.write(struct.pack('>i', imodModel.Objects[iObject].nSurfaces))





