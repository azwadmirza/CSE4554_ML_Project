def __virtual__():
    '''
    Only load this module if the ca config options are set
    '''
    if HAS_SSL and LooseVersion(OpenSSL_version) < LooseVersion('0.14'):
        if __opts__.get('ca.cert_base_path', None):
            return True
        else:
            log.error('tls module not loaded: ca.cert_base_path not set')
            return False
    else:
        return False, ['PyOpenSSL version 0.14 or later  must be installed before '
                       ' this module can be used.']