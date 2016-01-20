def ImodCmd(imodModel, cmdStr):
    from .ImodModel import ImodModel
    from .ImodWrite import ImodWrite
    from subprocess import call
    import os
    import random
    import string
    fname = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))
    ImodWrite(imodModel, fname)
    cmd = cmdStr + ' ' + fname + ' ' + fname
    call(cmd.split())
    imodModel = ImodModel(fname)
    os.remove(fname)
    os.remove(fname + '~')
    return imodModel

def is_integer(var, varStr):
    if not isinstance(var, (int, long)):
        raise ValueError('{0} must be an integer.'.format(varStr))
    else:
        return

def is_string(var, varStr):
    if not isinstance(var, str):
        raise ValueError('{0} must be a string.'.format(varStr))
    else:
        return

def set_bit(v, index, x):
    """
    http://stackoverflow.com/questions/12173774/modify-bits-in-an-integer-
    in-python
    """
    mask = 1 << index
    v &= ~mask
    if x:
        v |= mask
    return v
