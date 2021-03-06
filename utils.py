def ImodCmd(imodModel, cmdStr, return_output = False):
    from .ImodModel import ImodModel
    from .ImodWrite import ImodWrite
    import subprocess
    import os
    # Set name for temp output to a random 30 character string
    fname = random_filename(30)
    #fname = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))

    # Write the ImodModel object to disk
    ImodWrite(imodModel, fname)

    # Run the command
    cmd = cmdStr + ' ' + fname + ' ' + fname
    if return_output:
        proc = subprocess.Popen(cmd.split(), stdout = subprocess.PIPE)
    subprocess.call(cmd.split())

    # Load the output file as an ImodModel object
    imodModel = ImodModel(fname)

    # Cleanup temp files
    os.remove(fname)
    if os.path.isfile(fname + '~'):
        os.remove(fname + '~')

    if return_output:
        return imodModel, proc.stdout
    else:
        return imodModel

def random_filename(length):
    import random 
    import string
    fname = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))
    return fname

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

def get_bit(byteval, idx):
    return ((byteval&(1<<idx))!=0);
