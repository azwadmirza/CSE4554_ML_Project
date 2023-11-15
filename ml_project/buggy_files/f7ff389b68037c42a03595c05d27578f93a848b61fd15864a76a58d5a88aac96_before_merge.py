def create_cert_binding(name, site, hostheader='', ipaddress='*', port=443,
                        sslflags=0):
    '''
    Assign a certificate to an IIS Web Binding.

    .. versionadded:: 2016.11.0

    .. note::

        The web binding that the certificate is being assigned to must already
        exist.

    Args:
        name (str): The thumbprint of the certificate.
        site (str): The IIS site name.
        hostheader (str): The host header of the binding.
        ipaddress (str): The IP address of the binding.
        port (int): The TCP port of the binding.
        sslflags (int): Flags representing certificate type and certificate storage of the binding.

    Returns:
        bool: True if successful, otherwise False

    CLI Example:

    .. code-block:: bash

        salt '*' win_iis.create_cert_binding name='AAA000' site='site0' hostheader='example.com' ipaddress='*' port='443'
    '''
    name = str(name).upper()
    binding_info = _get_binding_info(hostheader, ipaddress, port)

    if _iisVersion() < 8:
        # IIS 7.5 and earlier don't support SNI for HTTPS, therefore cert bindings don't contain the host header
        binding_info = binding_info.rpartition(':')[0] + ':'

    binding_path = r"IIS:\SslBindings\{0}".format(binding_info.replace(':', '!'))

    if sslflags not in _VALID_SSL_FLAGS:
        message = ("Invalid sslflags '{0}' specified. Valid sslflags range: "
                   "{1}..{2}").format(sslflags, _VALID_SSL_FLAGS[0],
                                      _VALID_SSL_FLAGS[-1])
        raise SaltInvocationError(message)

    # Verify that the target binding exists.
    current_bindings = list_bindings(site)

    if binding_info not in current_bindings:
        log.error('Binding not present: {0}'.format(binding_info))
        return False

    # Check to see if the certificate is already assigned.
    current_name = None

    for current_binding in current_bindings:
        if binding_info == current_binding:
            current_name = current_bindings[current_binding]['certificatehash']

    log.debug('Current certificate thumbprint: {0}'.format(current_name))
    log.debug('New certificate thumbprint: {0}'.format(name))

    if name == current_name:
        log.debug('Certificate already present for binding: {0}'.format(name))
        return True

    # Verify that the certificate exists.
    certs = _list_certs()

    if name not in certs:
        log.error('Certificate not present: {0}'.format(name))
        return False

    if _iisVersion() < 8:
        # IIS 7.5 and earlier have different syntax for associating a certificate with a site
        # Modify IP spec to IIS 7.5 format
        iis7path = binding_path.replace(r"\*!", "\\0.0.0.0!")

        ps_cmd = ['New-Item',
                  '-Path', "'{0}'".format(iis7path),
                  '-Thumbprint', "'{0}'".format(name)]
    else:
        ps_cmd = ['New-Item',
                  '-Path', "'{0}'".format(binding_path),
                  '-Thumbprint', "'{0}'".format(name),
                  '-SSLFlags', '{0}'.format(sslflags)]

    cmd_ret = _srvmgr(ps_cmd)

    if cmd_ret['retcode'] != 0:
        msg = 'Unable to create certificate binding: {0}\nError: {1}' \
              ''.format(name, cmd_ret['stderr'])
        raise CommandExecutionError(msg)

    new_cert_bindings = list_cert_bindings(site)

    if binding_info not in new_cert_bindings:
        log.error('Binding not present: {0}'.format(binding_info))
        return False

    if name == new_cert_bindings[binding_info]['certificatehash']:
        log.debug('Certificate binding created successfully: {0}'.format(name))
        return True

    log.error('Unable to create certificate binding: {0}'.format(name))

    return False