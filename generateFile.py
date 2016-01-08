from .ImodModel import ImodModel
from .ImodObject import ImodObject
from .ImodWrite import ImodWrite

def blankTrainingModel(filename):
    """
    Creates a blank model file to be used for generating CHM training images
    and labels using IMOD. The output model file can be loaded on any MRC
    file, regardless of size or offsets.
    """
    # Create ImodModel class and two ImodObject sub-classes
    model = ImodModel()
    model.Objects.append(ImodObject())
    model.Objects.append(ImodObject())
    model.nObjects = 2

    # Set object properties of Object 1 (seed points)
    model.Objects[0].setName('Seed Points')
    model.Objects[0].setColor('0,1,0')
    model.Objects[0].setObjectType('scattered')
    model.Objects[0].setSymbolType('circle')
    model.Objects[0].setSymbolSize(10)
    model.Objects[0].setSymbolFillOn()

    # Set object properties of Object 2 (training contours)
    model.Objects[1].setName('Training Contours')
    model.Objects[1].setColor('0,1,1')
    model.Objects[1].setObjectType('closed')
    model.Objects[1].setLineWidth(2)

    # Write file
    ImodWrite(model, filename)
