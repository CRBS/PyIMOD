import struct
import timeit
import cv2 

import numpy as np

def run_slice(fname, nSlice):
    """
    Returns a numpy array consisting of a given slice of an input MRC file.

    Inputs
    ======
    fname  - Filename of the MRC file.
    nSlice - Slice number to extract from the MRC file.

    Returns
    =======
    imgSlice - Numpy array of the MRC slice.
    """

    with open(fname, mode = "rb") as fid:
        # Read the image dimensions, nx, ny, and nz from the MRC file header
        nx = struct.unpack('<i', fid.read(4))[0]
        ny = struct.unpack('<i', fid.read(4))[0]
        nz = struct.unpack('<i', fid.read(4))[0]

        # Seek to the proper location in the binary file
        fid.seek(1024 + (nx * ny) * (nSlice - 1) ,0) 

        # Get the Numpy array, assuming the MRC file is 8-bit, unsigned
        imgSlice = np.fromfile(fid, dtype = np.uint8, count = nx * ny) 

    # Reshape the Numpy array into the proper dimensions
    imgSlice = np.reshape(imgSlice, [ny, nx])

    # Flip the Numpy array vertically to account for the difference in indexing
    # between Numpy and IMOD.
    imgSlice = np.flipud(imgSlice)

    return imgSlice    
