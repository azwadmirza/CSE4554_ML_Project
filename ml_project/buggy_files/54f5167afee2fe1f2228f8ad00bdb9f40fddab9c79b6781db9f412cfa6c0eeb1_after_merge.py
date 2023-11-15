def __virtual__():
    '''
    Only load this module if right version of sleekxmpp is installed on this minion.
    '''
    min_version = '1.3.1'
    if HAS_LIBS:
        import sleekxmpp
        # Certain XMPP functionaility we're using doesn't work with versions under 1.3.1
        sleekxmpp_version = distutils.version.LooseVersion(sleekxmpp.__version__)
        valid_version = distutils.version.LooseVersion(min_version)
        if sleekxmpp_version >= valid_version:
            return __virtualname__
    return False, 'Could not import xmpp returner; sleekxmpp python client is not ' \
                  'installed or is older than version \'{0}\'.'.format(min_version)