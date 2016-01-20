from .ImodModel import ImodModel
from .ImodObject import ImodObject
from .ImodWrite import ImodWrite
from .utils import ImodCmd

def blankTrainingModel(filename = None):
    """
    Creates a blank model file to be used for generating CHM training images
    and labels using IMOD. The output model file can be loaded on any MRC
    file, regardless of size or offsets.
    """
    # Create ImodModel class and two ImodObject sub-classes
    model = ImodModel()
    model.addObject()
    model.addObject()

    # Set object properties of Object 1 (seed points)
    model.Objects[0].setName('Seed Points')
    model.Objects[0].setColor(0, 1, 0)
    model.Objects[0].setObjectType('scattered')
    model.Objects[0].setSymbolType('circle')
    model.Objects[0].setSymbolSize(10)
    model.Objects[0].setSymbolFillOn()

    # Set object properties of Object 2 (training contours)
    model.Objects[1].setName('Training Contours')
    model.Objects[1].setColor(0, 1, 1)
    model.Objects[1].setObjectType('closed')
    model.Objects[1].setLineWidth(2)

    # Write or return file
    if filename:
        ImodWrite(model, filename)
    else:
        return model

def tutorialModel(filename = None):
    """
    Creates a model file used in pyimod tutorials. Model file containts 25
    objects consisting of spheres and cubes of various sizes and positions.
    """
    model = ImodModel()
    model.setImageSize(1000, 1000, 1000)
    model.setPixelSizeXY(4)
    model.setPixelSizeZ(4)
    model.setUnits('nm')

    # Make big central sphere
    model.genSphereObject([500, 500, 500], 200, 100)

    # Make small, radius 50 spheres at 10 defined locations
    centers = [[700, 700, 700], [700, 800, 400], [300, 300, 500], 
        [450, 300, 100], [100, 100, 100], [850, 200, 600], [400, 700, 300],
        [800, 100, 700], [200, 900, 400]]
    [model.genSphereObject(x, 50, 25) for x in centers]

    # Make medium, radius 100 spheres at 10 defined locations
    centers = [[200, 200, 400], [150, 750, 800], [900, 500, 500],
        [800, 350, 350], [500, 100, 100]]
    [model.genSphereObject(x, 100, 50) for x in centers]

    # Make small, width 50 cubes at 5 defined locations
    centers = [[150, 500, 500], [850, 900, 850], [700, 200, 200],
        [850, 150, 800], [500, 500, 800]]
    [model.genCubeObject(x, 50) for x in centers]

    # Make medium, width 100 cubes at 5 defined locations
    centers = [[450, 850, 700], [800, 500, 850], [150, 500, 250],
        [750, 800, 200], [250, 200, 800]]
    [model.genCubeObject(x, 100) for x in centers]

    # Mesh all objects, with capping turned on
    model = ImodCmd(model, 'imodmesh -C')
  
    if filename:
        ImodWrite(model, filename)
    else: 
        return model 
