from .utils import is_string

def ImodExport(input, tag, **kwargs):
    iObject = kwargs.get('object', 0)

    is_string(tag, 'Export tag')
    objType = type(input).__name__
    print objType
    if objType == 'ImodModel':
        if iObject:
            mesh = get_mesh(input, iObject)
        else:
            raise ValueError('Must specify object number with object kwarg.')
    elif objType == 'ImodMesh':
        mesh = input 
    else:
        raise ValueError('input is not a valid class type.')

    if tag.lower() == 'vrml' or tag.lower() == 'wrl':
        print "VRML"

def get_mesh(imodModel, iObject):
    iObject-=1
    nObjects = imodModel.nObjects
    if iObject > nObjects:
        raise ValueError('Value specified by object kwarg exceeds nObjects.')
    nMeshes = imodModel.Objects[iObject].nMeshes
    if nMeshes > 1:
        raise ValueError('Object {0} contains > 1 mesh.'.format(iObject+1))
    mesh = imodModel.Objects[iObject].Meshes[0]
    return mesh    
