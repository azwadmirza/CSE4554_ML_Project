def add_service_certificate(kwargs=None, conn=None, call=None):
    '''
    .. versionadded:: 2015.8.0

    Add a new service certificate

    CLI Example:

    .. code-block:: bash

        salt-cloud -f add_service_certificate my-azure name=my_service_certificate \\
            data='...CERT_DATA...' certificate_format=sha1 password=verybadpass
    '''
    if call != 'function':
        raise SaltCloudSystemExit(
            'The add_service_certificate function must be called with -f or --function.'
        )

    if not conn:
        conn = get_conn()

    if kwargs is None:
        kwargs = {}

    if 'name' not in kwargs:
        raise SaltCloudSystemExit('A name must be specified as "name"')

    if 'data' not in kwargs:
        raise SaltCloudSystemExit('Certificate data must be specified as "data"')

    if 'certificate_format' not in kwargs:
        raise SaltCloudSystemExit('A certificate_format must be specified as "certificate_format"')

    if 'password' not in kwargs:
        raise SaltCloudSystemExit('A password must be specified as "password"')

    try:
        data = conn.add_service_certificate(
            kwargs['name'],
            kwargs['data'],
            kwargs['certificate_format'],
            kwargs['password'],
        )
        return {'Success': 'The service certificate was successfully added'}
    except WindowsAzureConflictError as exc:
        return {'Error': 'There was a Conflict. This usually means that the service certificate already exists.'}