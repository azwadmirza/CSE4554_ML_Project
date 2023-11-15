def import_cert(name, cert_format=_DEFAULT_FORMAT, context=_DEFAULT_CONTEXT, store=_DEFAULT_STORE,
                exportable=True, password='', saltenv='base'):
    '''
    Import the certificate file into the given certificate store.

    :param str name: The path of the certificate file to import.
    :param str cert_format: The certificate format. Specify 'cer' for X.509, or 'pfx' for PKCS #12.
    :param str context: The name of the certificate store location context.
    :param str store: The name of the certificate store.
    :param bool exportable: Mark the certificate as exportable. Only applicable to pfx format.
    :param str password: The password of the certificate. Only applicable to pfx format.
    :param str saltenv: The environment the file resides in.

    Example of usage with only the required arguments:

    .. code-block:: yaml

        site0-cert-imported:
            win_pki.import_cert:
                - name: salt://win/webserver/certs/site0.cer

    Example of usage specifying all available arguments:

    .. code-block:: yaml

        site0-cert-imported:
            win_pki.import_cert:
                - name: salt://win/webserver/certs/site0.pfx
                - cert_format: pfx
                - context: LocalMachine
                - store: My
                - exportable: True
                - password: TestPassword
                - saltenv: base
    '''
    ret = {'name': name,
           'changes': dict(),
           'comment': str(),
           'result': None}

    store_path = r'Cert:\{0}\{1}'.format(context, store)

    cached_source_path = __salt__['cp.cache_file'](name, saltenv)
    current_certs = __salt__['win_pki.get_certs'](context=context, store=store)
    cert_props = __salt__['win_pki.get_cert_file'](name=cached_source_path)

    if cert_props['thumbprint'] in current_certs:
        ret['comment'] = ("Certificate '{0}' already contained in store:"
                          ' {1}').format(cert_props['thumbprint'], store_path)
        ret['result'] = True
    elif __opts__['test']:
        ret['comment'] = ("Certificate '{0}' will be imported into store:"
                          ' {1}').format(cert_props['thumbprint'], store_path)
        ret['changes'] = {'old': None,
                          'new': cert_props['thumbprint']}
    else:
        ret['changes'] = {'old': None,
                          'new': cert_props['thumbprint']}
        ret['result'] = __salt__['win_pki.import_cert'](name=name, cert_format=cert_format,
                                                        context=context, store=store,
                                                        exportable=exportable, password=password,
                                                        saltenv=saltenv)
        if ret['result']:
            ret['comment'] = ("Certificate '{0}' imported into store:"
                              ' {1}').format(cert_props['thumbprint'], store_path)
        else:
            ret['comment'] = ("Certificate '{0}' unable to be imported into store:"
                              ' {1}').format(cert_props['thumbprint'], store_path)
    return ret