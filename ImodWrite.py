import struct

def ImodWrite(imodModel, fname):
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
    
def writeModelHeader(imodModel, fid):
    tag = 'IMOD' + imodModel.version
    nChar = len(imodModel.name)
    nameStr = imodModel.name + struct.pack('>B', 0) * (128 - nChar)
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
    fid.write(struct.pack('>f', imodModel.pixelSizeXY))
    fid.write(struct.pack('>i', imodModel.units))
    fid.write(struct.pack('>i', imodModel.csum))
    fid.write(struct.pack('>f', imodModel.alpha))
    fid.write(struct.pack('>f', imodModel.beta))
    fid.write(struct.pack('>f', imodModel.gamma))

def writeObjectHeader(imodModel, iObject, fid):
    fid.write('OBJT')
    name = imodModel.Objects[iObject].name
    nChar = len(name)
    tagStr = name + struct.pack('>B', 0) * (128 - nChar)
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

def writeContour(imodModel, iObject, iContour, fid):
    tagStr = 'CONT'
    fid.write(tagStr)
    fid.write(struct.pack('>i', imodModel.Objects[iObject].Contours[iContour].nPoints))
    fid.write(struct.pack('>I', imodModel.Objects[iObject].Contours[iContour].flags))
    fid.write(struct.pack('>i', imodModel.Objects[iObject].Contours[iContour].type))
    fid.write(struct.pack('>i', imodModel.Objects[iObject].Contours[iContour].iSurface))
    fid.write("".join([struct.pack('>f', x) for x in imodModel.Objects[iObject].Contours[iContour].points]))

def writeMesh(imodModel, iObject, iMesh, fid):
    tagStr = 'MESH'
    fid.write(tagStr)
    fid.write(struct.pack('>i', imodModel.Objects[iObject].Meshes[iMesh].nVertices))
    fid.write(struct.pack('>i', imodModel.Objects[iObject].Meshes[iMesh].nIndices))
    fid.write(struct.pack('>I', imodModel.Objects[iObject].Meshes[iMesh].flag))
    fid.write(struct.pack('>h', imodModel.Objects[iObject].Meshes[iMesh].type))
    fid.write(struct.pack('>h', imodModel.Objects[iObject].Meshes[iMesh].pad))
    fid.write("".join([struct.pack('>f', x) for x in imodModel.Objects[iObject].Meshes[iMesh].vertices]))
    fid.write("".join([struct.pack('>i', x) for x in imodModel.Objects[iObject].Meshes[iMesh].indices]))

def writeIMAT(imodModel, iObject, fid):
    tagStr = 'IMAT'
    fid.write(tagStr)
    fid.write(struct.pack('>i', 16))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].ambient))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].diffuse))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].specular))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].shininess))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].fillred))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].fillgreen))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].fillblue))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].quality))
    fid.write(struct.pack('>l', imodModel.Objects[iObject].mat2))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].valblack))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].valwhite))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].matflags2))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].mat3b3))

def writeChunk(imodModel, iObject, fid):
    nChunkBytes = imodModel.Objects[iObject].nChunkBytes
    fid.write(struct.pack('>i', imodModel.Objects[iObject].chunkID))
    fid.write(struct.pack('>i', nChunkBytes))
    fid.write(struct.pack('>B', 0) * nChunkBytes)

