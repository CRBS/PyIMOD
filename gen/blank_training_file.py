from .ImodModel import ImodModel
from .ImodObject import ImodObject

def blank_training_file():
    model = ImodModel()
    model.Objects.append(ImodObject())
    model.Objects.append(ImodObject())
    model.nObjects = 2

    model.Objects[0].setColor('0,1,0')

    model.Objects[1].setLineWidth(2)
    model.Objects[1].setColor('0,1,1')

