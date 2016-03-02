import subprocess
import numpy as np

def imodinfo_e(fname, iObj, ncont):
    """
    Runs imodinfo with the -e flag for a given object of the input model file.
    This will output metrics related to the ellipticity of all contours in the
    object, including: (1) the contour's semi-major and semi-minor axes, (2)
    the eccentricity, and (3) the long angle. These are stored to an array,
    with one line for each contour.

    Inputs
    ======
    fname - Filename of the IMOD model file to load.
    iObj  - Object number to analyze of the file specified by fname.
    ncont - Number of contours in the object

    Returns
    =======
    M - A numpy array of size (ncont x 5), in which the metrics of each contour
        are stored to their corresponding numbered lines. The metrics stored
        are: (1) Semi-major axis length, (2) semi-minor axis length, (3) the
        ratio of semi-major to semi-minor, (4) eccentricity, and (5) long angle.
    """

    # Run the command and get its output
    cmd = "imodinfo -e -o {0} {1}".format(iObj + 1, fname)
    proc = subprocess.Popen(cmd.split(), stdout = subprocess.PIPE)

    # Initialize an empty array to store metrics in
    M = np.zeros([ncont, 5])

    data_switch = 0
    C = 1
    for line in proc.stdout:
        # Initialize data storing after the imodinfo header line
        if not data_switch and "semi-major" in line:
            data_switch = 1
        elif data_switch and C <= ncont:
            line = line.split()
            # If C is less than the # of contours and the line contains
            # 'Mean', this means some contours were not computed properly.
            # Not sure why this happens, but when it does, they are 
            # completely skipped in the imodinfo output. When this occurs,
            # store NaNs to the array. Future functions will interpret these
            # NaNs as belonging toskipped contours.
            if str(line[0]) == 'Mean':
                delta = ncont - C + 1
                for i in range(delta):
                    M[C-1,:] = np.nan
                    C+=1
                continue
            # Likewise, if the contour number of the current line is not the
            # same as C, a contour has been skipped. Store a line of NaNs.
            if C != int(line[0]):
                delta = int(line[0]) - C
                for i in range(delta):
                    M[C-1,:] = np.nan
                    C+=1
            # Otherwise, store the correct data to the current line of the 
            # array M. Data stored are: (1) Semi-major, (2) Semi-minor, (3)
            # Ratio of semi-major to semi-minor, (4) eccentricity, and (5)
            # long angle.
            if C <= ncont:
                M[C-1,0] = float(line[4])
                M[C-1,1] = float(line[5])
                M[C-1,2] = M[C-1,0] / M[C-1,1]
                M[C-1,3] = float(line[6])
                M[C-1,4] = float(line[7])
                C+=1
    return M

def imodinfo_v(fname, iObj, ncont):
    """
    Runs imodinfo with the -v flag for a given object of the input model file.
    This will output a host of metrics for every contour in the object,
    including: (1) The number of points, (2) the closed length, (3) the open
    length, (4) the contour enclosed area, (5) the contour's center of mass,
    (6) the contour's circularity, (7) orientation angle, (8) ellipticity, (9)
    length, (10) width, (11) aspect ratio, (12) mesh volume, and (13) mesh
    surface area. Items 1-11 are stored to a numpy array, in which each line 
    corresponds to the metrics for its numbered contour.

    Inputs
    ======
    fname - Filename of the IMOD model file to load.
    iObj  - Object number to analyze of the file specified by fname.
    ncont - Number of contours in the object

    Returns
    =======
    M      - A numpy array of size (ncont x 13), in which the metrics of each
             contour are stored to their corresponding numbered lines.
    volume - Mesh volume of the entire object, given in microns cubed.
    sa     - Mesh surface area of the entire object, given in microns cubed.
    """

    # Run the command and get its output
    cmd = "imodinfo -v -o {0} {1}".format(iObj + 1, fname)
    proc = subprocess.Popen(cmd.split(), stdout = subprocess.PIPE)

    # Initialize an empty array to store metrics in
    M = np.zeros([ncont, 13])

    # Loop over all contours, and extract and store their metrics. Volume
    # and surface area are stored to separate variables, as they are given
    # for the whole object, rather than individual contours.
    C = -1
    for line in proc.stdout:
        if "CONTOUR" in line:
            C+=1
            M[C,0] = line.split()[2] #N points
        elif "Closed/Open length" in line:
            M[C,1] = line.split()[3] #Closed length
            M[C,2] = line.split()[5] #Open length
        elif "Enclosed Area" in line:
            M[C,3] = line.split()[3] #Area
        elif "Center of Mass" in line:
            M[C,4] = line.split()[4][1:-1] #Centroid X
            M[C,5] = line.split()[5][0:-1] #Centroid Y
            M[C,6] = line.split()[6][0:-1] #Centroid Z
        elif "Circle" in line:
            M[C,7] = line.split()[2] #Circle
        elif "Orientation" in line:
            M[C,8] = line.split()[2] #Orientation
        elif "Ellipse" in line:
            M[C,9] = line.split()[2] #Ellipse
        elif "Length X Width" in line:
            M[C,10] = line.split()[4] #Length
            M[C,11] = line.split()[6] #Width
        elif "Aspect Ratio" in line:
            M[C,12] = line.split()[3] #Aspect Ratio
        elif "Total volume inside mesh" in line:
            volume = float(line.split()[5]) / (1000 ** 3) #Volume
        elif "Total mesh surface area" in line:
            sa = float(line.split()[5]) / (1000 ** 2) #Surface Area
    return M, volume, sa

def calc_delta_centroid(iObj, z, fv):
    """
    Analyzes the change in centroid position in (X, Y) across slices, and
    returns statistics for the whole object. Statistics computed are: (1) the
    maximum change in Euclidean distance between two slices, (2) the mean # 
    change across all slices, and (3) the variance of change.
    
    Inputs
    ======
    iObj - Object number.
    z    - List of z coordinate of every contour in the object.
    fv   - Feature vector to append metrics to.
    
    Returns
    =======
    fv   - Feature vector to append metrics to.
    """

    xc = []
    yc = []
    d = []
    for i in range(z[0], z[-1] + 1):
        idx = np.where(z == i)[0]
        pts = []

        # Get points of all contours at current Z value
        for j in idx:
            pts.extend(mod.Objects[iObj].Contours[j].points)

        # Compute centroid components for the current Z value. Append them to
        # the x and y centroid coordinate lists, xc and yc, respectively.
        if pts:
            Npts = int(len(pts) / 3)
            xci = sum([x * mod.pixelSizeXY / 1000 for x in pts[0::3]]) / Npts
            yci = sum([y * mod.pixelSizeXY / 1000 for y in pts[1::3]]) / Npts
        xc.append(xci)
        yc.append(yci)

        # Compute the Euclidean distance between the (X,Y) centroid coordinates
        # of successive slices. Append to the distance list, d.
        if len(xc) > 1:
            d.append(math.sqrt((xc[-1] - xc[-2]) ** 2 + (yc[-1] - yc[-2]) ** 2))

    # Append the maximum distance, mean distance, and variance of distance to
    # the feature vector.
    fv.append(np.max(d))
    fv.append(np.mean(d))
    fv.append(np.var(d))
    return fv

def calc_centroid_3d(iObj, fv):
    """
    Calculates the 3D centroid of the input object, as well as relevant
    metrics, such as the furthest distance from the centroid to the list of
    contour points. Centroid is calculated as the mean centroid. The following
    values are appended to the input feature vector: (1) Maximum Euclidean
    distance (in microns) from the centroid to the surface, (2) proportion of
    slices above the centroid, and (3) proportion of slices below the
    centroid.
   
    Inputs
    ======
    iObj - Object number.
    fv   - Feature vector to append metrics to.
   
    Returns
    =======
    fv - Feature vector with metrics appended.
    """

    # Get a list of all points in the object
    ncont = mod.Objects[iObj].nContours
    pts = []
    for iCont in range(ncont):
        pts.extend(mod.Objects[iObj].Contours[iCont].points)
    npts = int(len(pts) / 3)
    ptsx = [x * mod.pixelSizeXY / 1000 for x in pts[0::3]]
    ptsy = [y * mod.pixelSizeXY / 1000 for y in pts[1::3]]
    ptsz = [z * mod.pixelSizeZ / 1000 for z in pts[2::3]]

    # Compute the 3D centroid of the entire object
    xci = sum(ptsx) / npts
    yci = sum(ptsy) / npts
    zci = sum(ptsz) / npts

    # Compute the maximum distance
    d = []
    for iPt in range(npts):
        dx = (ptsx[iPt] - xci) ** 2
        dy = (ptsy[iPt] - yci) ** 2
        dz = (ptsz[iPt] - zci) ** 2
        d.append(math.sqrt(dx + dy + dz))

    # Compute the proportion of slices above and below the centroid slice
    idx1 = np.where(np.asarray(ptsz) > zci)[0]
    idx2 = np.where(np.asarray(ptsz) < zci)[0]
    nzabove = len(np.unique(np.asarray(ptsz)[idx1]))
    nzbelow = len(np.unique(np.asarray(ptsz)[idx2]))
    pzabove = nzabove / (nzabove + nzbelow + 1)
    pzbelow = nzbelow / (nzabove + nzbelow + 1)

    fv.append(np.max(d))
    fv.append(pzabove)
    fv.append(pzbelow)
    return fv
