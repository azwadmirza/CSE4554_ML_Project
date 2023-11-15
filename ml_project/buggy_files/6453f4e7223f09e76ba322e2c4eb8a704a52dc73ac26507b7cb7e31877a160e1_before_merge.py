def set_storage_container_metadata(kwargs=None, storage_conn=None, call=None):
    '''
    .. versionadded:: 2015.8.0

    Set a storage container's metadata

    CLI Example:

    .. code-block:: bash

        salt-cloud -f set_storage_container my-azure name=mycontainer \
            x_ms_meta_name_values='{"my_name": "my_value"}'

    name:
        Name of existing container.
    meta_name_values:
        A dict containing name, value for metadata.
        Example: {'category':'test'}
    lease_id:
        If specified, set_storage_container_metadata only succeeds if the
        container's lease is active and matches this ID.
    '''
    if call != 'function':
        raise SaltCloudSystemExit(
            'The create_storage_container function must be called with -f or --function.'
        )

    if kwargs is None:
        kwargs = {}

    if 'name' not in kwargs:
        raise SaltCloudSystemExit('An storage container name must be specified as "name"')

    x_ms_meta_name_values = yaml.safe_load(
        kwargs.get('meta_name_values', '')
    )

    if not storage_conn:
        storage_conn = get_storage_conn(conn_kwargs=kwargs)

    try:
        storage_conn.set_container_metadata(
            container_name=kwargs['name'],
            x_ms_meta_name_values=x_ms_meta_name_values,
            x_ms_lease_id=kwargs.get('lease_id', None),
        )
        return {'Success': 'The storage container was successfully updated'}
    except WindowsAzureConflictError as exc:
        return {'Error': 'There was a Conflict.'}