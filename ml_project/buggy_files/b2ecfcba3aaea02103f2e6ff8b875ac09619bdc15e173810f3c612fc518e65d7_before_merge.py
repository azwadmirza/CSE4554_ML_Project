def show_input_endpoint(kwargs=None, conn=None, call=None):
    '''
    .. versionadded:: 2015.8.0

    Show an input endpoint associated with the deployment

    CLI Example:

    .. code-block:: bash

        salt-cloud -f show_input_endpoint my-azure service=myservice \
            deployment=mydeployment name=SSH
    '''
    if call != 'function':
        raise SaltCloudSystemExit(
            'The show_input_endpoint function must be called with -f or --function.'
        )

    if kwargs is None:
        kwargs = {}

    if 'name' not in kwargs:
        raise SaltCloudSystemExit('An endpoint name must be specified as "name"')

    data = list_input_endpoints(kwargs=kwargs, call='function')
    return data.get(kwargs['name'], None)