def delete_management_certificate(kwargs=None, conn=None, call=None):
    '''
    .. versionadded:: 2015.8.0

    Delete a specific certificate associated with the management

    CLI Examples:

    .. code-block:: bash

        salt-cloud -f delete_management_certificate my-azure name=my_management_certificate \\
            thumbalgorithm=sha1 thumbprint=0123456789ABCDEF
    '''
    if call != 'function':
        raise SaltCloudSystemExit(
            'The delete_management_certificate function must be called with -f or --function.'
        )

    if kwargs is None:
        kwargs = {}

    if 'thumbprint' not in kwargs:
        raise SaltCloudSystemExit('A thumbprint must be specified as "thumbprint"')

    if not conn:
        conn = get_conn()

    try:
        data = conn.delete_management_certificate(kwargs['thumbprint'])
        return {'Success': 'The management certificate was successfully deleted'}
    except WindowsAzureMissingResourceError as exc:
        return {'Error': exc.message}