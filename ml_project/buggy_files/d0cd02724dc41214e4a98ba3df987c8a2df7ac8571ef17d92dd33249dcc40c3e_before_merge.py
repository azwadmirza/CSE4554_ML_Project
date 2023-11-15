def show_service_certificate(kwargs=None, conn=None, call=None):
    '''
    .. versionadded:: 2015.8.0

    Return information about a service certificate

    CLI Example:

    .. code-block:: bash

        salt-cloud -f show_service_certificate my-azure name=my_service_certificate \
            thumbalgorithm=sha1 thumbprint=0123456789ABCDEF
    '''
    if call != 'function':
        raise SaltCloudSystemExit(
            'The get_service_certificate function must be called with -f or --function.'
        )

    if not conn:
        conn = get_conn()

    if kwargs is None:
        kwargs = {}

    if 'name' not in kwargs:
        raise SaltCloudSystemExit('A service name must be specified as "name"')

    if 'thumbalgorithm' not in kwargs:
        raise SaltCloudSystemExit('A thumbalgorithm must be specified as "thumbalgorithm"')

    if 'thumbprint' not in kwargs:
        raise SaltCloudSystemExit('A thumbprint must be specified as "thumbprint"')

    data = conn.get_service_certificate(
        kwargs['name'],
        kwargs['thumbalgorithm'],
        kwargs['thumbprint'],
    )
    return object_to_dict(data)