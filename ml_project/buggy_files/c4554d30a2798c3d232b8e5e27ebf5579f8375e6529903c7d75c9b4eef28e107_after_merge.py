def import_cert(name,
                cert_format=_DEFAULT_FORMAT,
                context=_DEFAULT_CONTEXT,
                store=_DEFAULT_STORE,
                exportable=True,
                password='',
                saltenv='base'):
    '''
    Import the certificate file into the given certificate store.

    :param str name: The path of the certificate file to import.
    :param str cert_format: The certificate format. Specify 'cer' for X.509, or
        'pfx' for PKCS #12.
    :param str context: The name of the certificate store location context.
    :param str store: The name of the certificate store.
    :param bool exportable: Mark the certificate as exportable. Only applicable
        to pfx format.
    :param str password: The password of the certificate. Only applicable to pfx
        format. Note that if used interactively, the password will be seen by all minions.
        To protect the password, use a state and get the password from pillar.
    :param str saltenv: The environment the file resides in.

    :return: A boolean representing whether all changes succeeded.
    :rtype: bool

    CLI Example:

    .. code-block:: bash

        salt '*' win_pki.import_cert name='salt://cert.cer'
    '''
    cmd = list()
    thumbprint = None
    store_path = r'Cert:\{0}\{1}'.format(context, store)
    cert_format = cert_format.lower()

    _validate_cert_format(name=cert_format)

    cached_source_path = __salt__['cp.cache_file'](name, saltenv)

    if not cached_source_path:
        _LOG.error('Unable to get cached copy of file: %s', name)
        return False

    if password:
        cert_props = get_cert_file(name=cached_source_path, cert_format=cert_format, password=password)
    else:
        cert_props = get_cert_file(name=cached_source_path, cert_format=cert_format)

    current_certs = get_certs(context=context, store=store)

    if cert_props['thumbprint'] in current_certs:
        _LOG.debug("Certificate thumbprint '%s' already present in store: %s",
                   cert_props['thumbprint'], store_path)
        return True

    if cert_format == 'pfx':
        # In instances where an empty password is needed, we use a
        # System.Security.SecureString object since ConvertTo-SecureString will
        # not convert an empty string.
        if password:
            cmd.append(r"$Password = ConvertTo-SecureString "
                       r"-String '{0}'".format(password))
            cmd.append(' -AsPlainText -Force; ')
        else:
            cmd.append('$Password = New-Object System.Security.SecureString; ')

        cmd.append(r"Import-PfxCertificate "
                   r"-FilePath '{0}'".format(cached_source_path))
        cmd.append(r" -CertStoreLocation '{0}'".format(store_path))
        cmd.append(r" -Password $Password")

        if exportable:
            cmd.append(' -Exportable')
    else:
        cmd.append(r"Import-Certificate "
                   r"-FilePath '{0}'".format(cached_source_path))
        cmd.append(r" -CertStoreLocation '{0}'".format(store_path))

    _cmd_run(cmd=str().join(cmd))

    new_certs = get_certs(context=context, store=store)

    for new_cert in new_certs:
        if new_cert not in current_certs:
            thumbprint = new_cert

    if thumbprint:
        _LOG.debug('Certificate imported successfully: %s', name)
        return True
    _LOG.error('Unable to import certificate: %s', name)
    return False