def create_csr(path=None, text=False, **kwargs):
    '''
    Create a certificate signing request.

    path:
        Path to write the certificate to.

    text:
        If ``True``, return the PEM text without writing to a file. Default ``False``.

    algorithm:
        The hashing algorithm to be used for signing this request. Defaults to sha256.

    kwargs:
        The subject, extension and version arguments from
        :mod:`x509.create_certificate <salt.modules.x509.create_certificate>` can be used.

    CLI Example:

    .. code-block:: bash

        salt '*' x509.create_csr path=/etc/pki/myca.csr public_key='/etc/pki/myca.key' CN='My Cert
    '''

    if not path and not text:
        raise salt.exceptions.SaltInvocationError('Either path or text must be specified.')
    if path and text:
        raise salt.exceptions.SaltInvocationError('Either path or text must be specified, not both.')

    csr = M2Crypto.X509.Request()
    subject = csr.get_subject()

    for prop, default in six.iteritems(CERT_DEFAULTS):
        if prop not in kwargs:
            kwargs[prop] = default

    csr.set_version(kwargs['version'] - 1)

    if 'private_key' not in kwargs and 'public_key' in kwargs:
        kwargs['private_key'] = kwargs['public_key']
        log.warning("OpenSSL no longer allows working with non-signed CSRs. A private_key must be specified. Attempting to use public_key as private_key")

    if 'private_key' not in kwargs not in kwargs:
        raise salt.exceptions.SaltInvocationError('private_key is required')

    if 'public_key' not in kwargs:
        kwargs['public_key'] = kwargs['private_key']

    csr.set_pubkey(get_public_key(kwargs['public_key'], asObj=True))

    for entry, num in six.iteritems(subject.nid):                  # pylint: disable=unused-variable
        if entry in kwargs:
            setattr(subject, entry, kwargs[entry])

    extstack = M2Crypto.X509.X509_Extension_Stack()
    for extname, extlongname in six.iteritems(EXT_NAME_MAPPINGS):
        if extname not in kwargs and extlongname not in kwargs:
            continue

        extval = kwargs[extname] or kwargs[extlongname]

        critical = False
        if extval.startswith('critical '):
            critical = True
            extval = extval[9:]

        issuer = None
        ext = _new_extension(name=extname, value=extval, critical=critical, issuer=issuer)
        if not ext.x509_ext:
            log.info('Invalid X509v3 Extension. {0}: {1}'.format(extname, extval))
            continue

        extstack.push(ext)

    csr.add_extensions(extstack)

    csr.sign(_get_private_key_obj(kwargs['private_key']), kwargs['algorithm'])

    if path:
        return write_pem(text=csr.as_pem(), path=path,
                pem_type='CERTIFICATE REQUEST')
    else:
        return csr.as_pem()