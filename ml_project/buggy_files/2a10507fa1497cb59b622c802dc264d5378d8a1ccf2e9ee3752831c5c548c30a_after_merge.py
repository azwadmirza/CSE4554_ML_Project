def create_snapshot(kwargs=None, call=None, wait_to_finish=False):
    '''
    Create a snapshot.

    volume_id
        The ID of the Volume from which to create a snapshot.

    description
        The optional description of the snapshot.

    CLI Exampe:

    .. code-block:: bash

        salt-cloud -f create_snapshot my-ec2-config volume_id=vol-351d8826
        salt-cloud -f create_snapshot my-ec2-config volume_id=vol-351d8826 \\
            description="My Snapshot Description"
    '''
    if call != 'function':
        raise SaltCloudSystemExit(
            'The create_snapshot function must be called with -f '
            'or --function.'
        )

    if kwargs is None:
        kwargs = {}

    volume_id = kwargs.get('volume_id', None)
    description = kwargs.get('description', '')

    if volume_id is None:
        raise SaltCloudSystemExit(
            'A volume_id must be specified to create a snapshot.'
        )

    params = {'Action': 'CreateSnapshot',
              'VolumeId': volume_id,
              'Description': description}

    log.debug(params)

    data = aws.query(params,
                     return_url=True,
                     return_root=True,
                     location=get_location(),
                     provider=get_provider(),
                     opts=__opts__,
                     sigver='4')[0]

    r_data = {}
    for d in data:
        for k, v in d.items():
            r_data[k] = v
    snapshot_id = r_data['snapshotId']

    # Waits till volume is available
    if wait_to_finish:
        salt.utils.cloud.run_func_until_ret_arg(fun=describe_snapshots,
                                                kwargs={'snapshot_id': snapshot_id},
                                                fun_call=call,
                                                argument_being_watched='status',
                                                required_argument_response='completed')

    return data