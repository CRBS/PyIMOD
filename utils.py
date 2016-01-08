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
