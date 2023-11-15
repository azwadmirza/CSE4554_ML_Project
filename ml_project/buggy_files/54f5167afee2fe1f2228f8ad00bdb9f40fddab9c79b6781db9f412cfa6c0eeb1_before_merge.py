def __virtual__():
    '''
    Only load this module if right version of sleekxmpp is installed on this minion.
    '''
    if HAS_LIBS:
        import sleekxmpp
        # Certain XMPP functionaility we're using doesn't work with versions under 1.3.1
        sleekxmpp_version = distutils.version.LooseVersion(sleekxmpp.__version__)
        valid_version = distutils.version.LooseVersion('1.3.1')
        if sleekxmpp_version >= valid_version:
            return __virtualname__
    return False