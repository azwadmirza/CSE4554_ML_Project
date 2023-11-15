def add_management_certificate(kwargs=None, conn=None, call=None):
    '''
    .. versionadded:: 2015.8.0

    Add a new management certificate

    CLI Example:

    .. code-block:: bash

        salt-cloud -f add_management_certificate my-azure public_key='...PUBKEY...' \
            thumbprint=0123456789ABCDEF data='...CERT_DATA...'
    '''
    if call != 'function':
        raise SaltCloudSystemExit(
            'The add_management_certificate function must be called with -f or --function.'
        )

    if not conn:
        conn = get_conn()

    if kwargs is None:
        kwargs = {}

    if 'public_key' not in kwargs:
        raise SaltCloudSystemExit('A public_key must be specified as "public_key"')

    if 'thumbprint' not in kwargs:
        raise SaltCloudSystemExit('A thumbprint must be specified as "thumbprint"')

    if 'data' not in kwargs:
        raise SaltCloudSystemExit('Certificate data must be specified as "data"')

    try:
        data = conn.add_management_certificate(
            kwargs['name'],
            kwargs['thumbprint'],
            kwargs['data'],
        )
        return {'Success': 'The management certificate was successfully added'}
    except WindowsAzureConflictError as exc:
        return {'Error': 'There was a Conflict. This usually means that the management certificate already exists.'}