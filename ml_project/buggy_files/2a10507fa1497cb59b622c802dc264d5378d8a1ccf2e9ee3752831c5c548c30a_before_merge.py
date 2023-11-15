def create_snapshot(kwargs=None, call=None, wait_to_finish=False):
    '''
    Create a snapshot
    '''
    if call != 'function':
        log.error(
            'The create_snapshot function must be called with -f '
            'or --function.'
        )
        return False

    if 'volume_id' not in kwargs:
        log.error('A volume_id must be specified to create a snapshot.')
        return False

    if 'description' not in kwargs:
        kwargs['description'] = ''

    params = {'Action': 'CreateSnapshot'}

    if 'volume_id' in kwargs:
        params['VolumeId'] = kwargs['volume_id']

    if 'description' in kwargs:
        params['Description'] = kwargs['description']

    log.debug(params)

    data = aws.query(params,
                     return_url=True,
                     location=get_location(),
                     provider=get_provider(),
                     opts=__opts__,
                     sigver='4')

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