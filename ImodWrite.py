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
            if imodModel.Objects[iObject].mepa_set:
                writeMEPA(imodModel, iObject, fid)

        # Handles the case in which there is a 4 byte VIEW chunk before the 
        # main VIEW chunk. In this case, write the chunk title ('VIEW'), the
        # number of bytes (4), and the cview value read from the file.
        if imodModel.view_4bytes == 1:
            fid.write('VIEW')
            fid.write(struct.pack('>i', 4))
            fid.write(struct.pack('>i', imodModel.view_4bytes_cview))    

        # Write the main VIEW chunk model-level header
        if imodModel.view_set:
            writeViewHeader(imodModel, fid)

            # Write each object's VIEW chunk
            for iObject in range(imodModel.view_objvsize):
                if imodModel.Objects[iObject].Views:
                    writeView(imodModel, iObject, fid)

        # Write MINX data, if it has been created or read.
        if imodModel.minx_set:
            writeMinx(imodModel, fid)

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
    try:
        fid.write(struct.pack('>I', imodModel.Objects[iObject].Contours[iContour].flags))
    except:
        fid.write(struct.pack('>I', 0))
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

def writeMEPA(imodModel, iObject, fid):
    fid.write('MEPA')
    fid.write(struct.pack('>i', imodModel.Objects[iObject].mepa_nBytes))
    [fid.write(struct.pack('>B', x)) for x in imodModel.Objects[iObject].mepa_byteString]

def writeViewHeader(imodModel, fid):
    fid.write('VIEW')
    fid.write(struct.pack('>i', 184 + imodModel.nObjects * 187))
    fid.write(struct.pack('>f', imodModel.view_fovy)) 
    fid.write(struct.pack('>f', imodModel.view_rad))
    fid.write(struct.pack('>f', imodModel.view_aspect))
    fid.write(struct.pack('>f', imodModel.view_cnear))
    fid.write(struct.pack('>f', imodModel.view_cfar))
    fid.write(struct.pack('>f', imodModel.view_rot_x))
    fid.write(struct.pack('>f', imodModel.view_rot_y))
    fid.write(struct.pack('>f', imodModel.view_rot_z))
    fid.write(struct.pack('>f', imodModel.view_trans_x))
    fid.write(struct.pack('>f', imodModel.view_trans_y))
    fid.write(struct.pack('>f', imodModel.view_trans_z)) 
    fid.write(struct.pack('>f', imodModel.view_scale_x))
    fid.write(struct.pack('>f', imodModel.view_scale_y))
    fid.write(struct.pack('>f', imodModel.view_scale_z))
    [fid.write(struct.pack('>f', x)) for x in imodModel.view_mat]
    fid.write(struct.pack('>i', imodModel.view_world))
    tag = imodModel.view_label
    nChar = len(tag)
    fid.write(tag + struct.pack('>B', 0) * (32 - nChar))
    fid.write(struct.pack('>f', imodModel.view_dcstart))
    fid.write(struct.pack('>f', imodModel.view_dcend))
    fid.write(struct.pack('>f', imodModel.view_lightx))
    fid.write(struct.pack('>f', imodModel.view_lighty))
    fid.write(struct.pack('>f', imodModel.view_plax))
    fid.write(struct.pack('>i', imodModel.view_objvsize)) #objvsize
    fid.write(struct.pack('>i', imodModel.view_objvsize * 187)) #bytesObjv

def writeView(imodModel, iObject, fid):
    fid.write(struct.pack('>I', imodModel.Objects[iObject].Views[0].flags))
    fid.write(struct.pack('>f', imodModel.Objects[iObject].Views[0].red))
    fid.write(struct.pack('>f', imodModel.Objects[iObject].Views[0].green))
    fid.write(struct.pack('>f', imodModel.Objects[iObject].Views[0].blue))
    fid.write(struct.pack('>i', imodModel.Objects[iObject].Views[0].pdrawsize))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].Views[0].linewidth))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].Views[0].linesty))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].Views[0].trans))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].Views[0].clips_count))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].Views[0].clips_flags))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].Views[0].clips_trans))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].Views[0].clips_plane))
    fid.write(struct.pack('>f', imodModel.Objects[iObject].Views[0].clips_normal_x))
    fid.write(struct.pack('>f', imodModel.Objects[iObject].Views[0].clips_normal_y))
    fid.write(struct.pack('>f', imodModel.Objects[iObject].Views[0].clips_normal_z))
    fid.write(struct.pack('>f', imodModel.Objects[iObject].Views[0].clips_points_x))
    fid.write(struct.pack('>f', imodModel.Objects[iObject].Views[0].clips_points_y))
    fid.write(struct.pack('>f', imodModel.Objects[iObject].Views[0].clips_points_z))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].Views[0].ambient))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].Views[0].diffuse))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].Views[0].specular))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].Views[0].shininess))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].Views[0].fillred))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].Views[0].fillgreen))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].Views[0].fillblue))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].Views[0].quality))
    fid.write(struct.pack('>I', imodModel.Objects[iObject].Views[0].mat2))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].Views[0].valblack))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].Views[0].valwhite))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].Views[0].mat3b2))
    fid.write(struct.pack('>B', imodModel.Objects[iObject].Views[0].mat3b3))
    [fid.write(struct.pack('>f', x)) for x in imodModel.Objects[iObject].Views[0].clips_normal]
    [fid.write(struct.pack('>f', x)) for x in imodModel.Objects[iObject].Views[0].clips_point] 

def writeMinx(imodModel, fid):
    fid.write('MINX')
    fid.write(struct.pack('>i', 72))
    [fid.write(struct.pack('>f', x)) for x in imodModel.minx_oscale]
    [fid.write(struct.pack('>f', x)) for x in imodModel.minx_otrans]
    [fid.write(struct.pack('>f', x)) for x in imodModel.minx_orot]
    [fid.write(struct.pack('>f', x)) for x in imodModel.minx_cscale]
    [fid.write(struct.pack('>f', x)) for x in imodModel.minx_ctrans]
    [fid.write(struct.pack('>f', x)) for x in imodModel.minx_crot]
