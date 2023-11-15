def _passphrase_callback(passphrase):
    '''
    Returns a callback function used to supply a passphrase for private keys
    '''
    def f(*args):
        return passphrase
    return f