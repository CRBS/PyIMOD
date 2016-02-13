#!/usr/bin/env python

from __future__ import division

import numpy as np
import time
import re

def get_adjacent_verts(seed, indices):
    # Find all triangles that contain the seed vertex
    tris_with_seed = np.where(indices == seed)[0]

    # Find all vertices of these triangles. Keep only the unique ones
    idx = []
    for i in tris_with_seed:
        idx = np.hstack([idx, indices[i]])
    idx = np.unique(idx).tolist()
    idx = [int(x) for x in idx]
    idx.remove(seed)
    return idx

file_shape = 'ShapeIndex2.am'
file_surf = 'GeometrySurface2.smooth.surf'
file_grad = 'Result.am'

##########
#
# Read files into numpy arrays
#
##########

# Import shape index scalar field
C = 0
K = 0
with open(file_shape, 'r') as fid:
    for line in fid:
        if re.match('^nNodes', line):
            nVert = int(line.split()[1])
            shapeIndex = np.zeros([nVert, 1])
        if re.match('^@1', line):
            C = 1
            continue
        if C and line.strip():
            shapeIndex[K] = float(line)
            K+=1 

# Import gradient vectors
C = 0
K = 0
with open(file_grad, 'r') as fid:
    for line in fid:
        if re.match('^nTriangles', line):
            nTri = int(line.split()[1])
            grad = np.zeros([nTri, 3])
        if re.match('^@1', line):
            C = 1
            continue
        if C and line.strip():
            vector = [np.absolute(float(x)) for x in line.split()]
            grad[K,] = vector
            #norm = np.linalg.norm(vector)
            #grad[K,] = [x / norm for x in vector]
            K+=1

# Import triangle vertices and indices
C = 0
with open(file_surf, 'r') as fid:
    for line in fid: 
        if re.match('^Vertices', line):
            nVert = int(line.split()[1])
            C = 1
            Kvert = 0
            continue

        if re.match('^Triangles', line):
            nInd = int(line.split()[1])
            C = 2
            Kind = 0
            continue

        if C == 1 and Kvert < nVert:
            coords = [float(x) for x in line.split()]
            try:
                vertices
            except NameError:
                vertices = np.array(coords)
            else:
                vertices = np.vstack([vertices, coords])   
            Kvert+=1 
        elif C == 1 and Kvert >= nVert:
            C = 0
            continue

        if C == 2 and Kind < nInd:
            inds = [int(x) for x in line.split()]
            try:
                indices
            except NameError:
                indices = np.array(inds)
            else:
                indices = np.vstack([indices, inds])
            Kind+=1
        elif C == 2 and Kind >= nInd:
            C = 0
            continue

##########
#
# Main
#
##########

nTri = indices.shape[0]
nVert = vertices.shape[0]

idx_keep = []

# Find all vertices with Shape Index > 0
vert_idx_pos = np.where(shapeIndex > 0)[0].tolist()
vert_idx_pos = [int(x) + 1 for x in vert_idx_pos]

nCluster = 0
while vert_idx_pos:
    # Set the seed vertex as the first entry
    vert_seed = vert_idx_pos[0]
    vert_check = [vert_seed]
    vert_keep = []

    while vert_check:
        # Find all vertices in triangles adjacent to the seed vertex
        vert_adj = get_adjacent_verts(vert_check[0], indices)
        vert_keep.append(vert_check[0])

        # If none of the adjacent vertices have a positive Shape Index,
        # then the seed vertex is an island. Break the loop and remove it.
        # If there is at least one adjacent vertex with a positive Shape
        # Index, add the seed vertex to the keep list and remove it from the
        # seed position of the check list.
        if not sum([x in vert_idx_pos for x in vert_adj]):
            break
        else:
            vert_check = vert_check[1:]

        # Append all adjacent vertices with positive Shape Indices to the
        # check list.
        for i in vert_adj:
            if (i in vert_idx_pos) and (i not in vert_check) and (i not in vert_keep):
                vert_check.append(i)

    for i in vert_keep:
        vert_idx_pos.remove(i)

    # Process the relevantly sized clusters
    if len(vert_keep) > 20:
        nCluster+=1
        nVertCluster = len(vert_keep)

        # Get a list of Shape Index values from the vertices
        K = 0
        sCluster = np.zeros([nVertCluster, 1]) 
        for i in vert_keep:
            sCluster[K] = shapeIndex[i - 1]
            K+=1

        # Get the triangles from vertices
        tri_keep = []
        for i in vert_keep:
            tris_with_vert = np.where(indices == i)[0]
            for j in tris_with_vert:
                idx = indices[j]
                if sum([x in vert_keep for x in idx]) == 3 and j not in tri_keep:
                    tri_keep.append(j)
        nTriCluster = len(tri_keep)

        # Get the gradients from the triangles. Take the magnitude of the
        # Shape Index gradient at each triangle face.
        magMinCluster = 1
        for i in tri_keep:
            gradi = grad[i,:]
            magClusteri = np.linalg.norm(gradi)
            if magClusteri < magMinCluster:
                magMinCluster = magClusteri
                imc = indices[i,:]

        print vertices[imc[0]-1,:]
        print vertices[imc[1]-1,:]
        print vertices[imc[2]-1,:]

        coordx = (vertices[imc[0]-1,0] + vertices[imc[1]-1,0] + vertices[imc[2]-1,0]) / 3
        coordy = (vertices[imc[0]-1,1] + vertices[imc[1]-1,1] + vertices[imc[2]-1,1]) / 3
        coordz = (vertices[imc[0]-1,2] + vertices[imc[1]-1,2] + vertices[imc[2]-1,2]) / 3   
            
        coordx = (coordx+999)/300
        coordy = coordy/300
        coordz = (coordz+14)/300

 
        # Print metrics
        print "Cluster {0}".format(nCluster)
        print "==========="
        print "# Vertices : {0}".format(nVertCluster)
        print "# Triangles: {0}".format(nTriCluster)
        print "S_min  : {0}".format(np.amin(sCluster))
        print "S_max  : {0}".format(np.amax(sCluster))
        print "S_mean : {0}".format(np.mean(sCluster))
        print "S_std  : {0}".format(np.std(sCluster))
        print "Min. gradient magnitude: {0}".format(magMinCluster)
        print "Coords: {0}, {1}, {2}".format(coordx, coordy, coordz)
        print ""

