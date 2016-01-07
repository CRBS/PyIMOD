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
