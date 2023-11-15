def show_affinity_group(kwargs=None, conn=None, call=None):
    '''
    .. versionadded:: 2015.8.0

    Show an affinity group associated with the account

    CLI Example:

    .. code-block:: bash

        salt-cloud -f show_affinity_group my-azure service=myservice \
            deployment=mydeployment name=SSH
    '''
    if call != 'function':
        raise SaltCloudSystemExit(
            'The show_affinity_group function must be called with -f or --function.'
        )

    if not conn:
        conn = get_conn()

    if kwargs is None:
        kwargs = {}

    if 'name' not in kwargs:
        raise SaltCloudSystemExit('An affinity group name must be specified as "name"')

    data = conn.get_affinity_group_properties(affinity_group_name=kwargs['name'])
    return object_to_dict(data)