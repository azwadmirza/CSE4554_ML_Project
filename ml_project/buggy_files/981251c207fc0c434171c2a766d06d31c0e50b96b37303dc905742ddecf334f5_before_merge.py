def delete_service_certificate(kwargs=None, conn=None, call=None):
    '''
    .. versionadded:: 2015.8.0

    Delete a specific certificate associated with the service

    CLI Examples:

    .. code-block:: bash

        salt-cloud -f delete_service_certificate my-azure name=my_service_certificate \
            thumbalgorithm=sha1 thumbprint=0123456789ABCDEF
    '''
    if call != 'function':
        raise SaltCloudSystemExit(
            'The delete_service_certificate function must be called with -f or --function.'
        )

    if kwargs is None:
        kwargs = {}

    if 'name' not in kwargs:
        raise SaltCloudSystemExit('A name must be specified as "name"')

    if 'thumbalgorithm' not in kwargs:
        raise SaltCloudSystemExit('A thumbalgorithm must be specified as "thumbalgorithm"')

    if 'thumbprint' not in kwargs:
        raise SaltCloudSystemExit('A thumbprint must be specified as "thumbprint"')

    if not conn:
        conn = get_conn()

    try:
        data = conn.delete_service_certificate(
            kwargs['name'],
            kwargs['thumbalgorithm'],
            kwargs['thumbprint'],
        )
        return {'Success': 'The service certificate was successfully deleted'}
    except WindowsAzureMissingResourceError as exc:
        return {'Error': exc.message}