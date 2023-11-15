def show_management_certificate(kwargs=None, conn=None, call=None):
    '''
    .. versionadded:: 2015.8.0

    Return information about a management_certificate

    CLI Example:

    .. code-block:: bash

        salt-cloud -f get_management_certificate my-azure name=my_management_certificate \
            thumbalgorithm=sha1 thumbprint=0123456789ABCDEF
    '''
    if call != 'function':
        raise SaltCloudSystemExit(
            'The get_management_certificate function must be called with -f or --function.'
        )

    if not conn:
        conn = get_conn()

    if kwargs is None:
        kwargs = {}

    if 'thumbprint' not in kwargs:
        raise SaltCloudSystemExit('A thumbprint must be specified as "thumbprint"')

    data = conn.get_management_certificate(kwargs['thumbprint'])
    return object_to_dict(data)