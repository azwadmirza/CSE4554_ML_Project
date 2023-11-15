def create_multiprocessing(parallel_data, queue=None):
    '''
    This function will be called from another process when running a map in
    parallel mode. The result from the create is always a json object.
    '''
    reinit_crypto()

    parallel_data['opts']['output'] = 'json'
    cloud = Cloud(parallel_data['opts'])
    try:
        output = cloud.create(
            parallel_data['profile'],
            local_master=parallel_data['local_master']
        )
    except SaltCloudException as exc:
        log.error(
            'Failed to deploy {0[name]!r}. Error: {1}'.format(
                parallel_data, exc
            ),
            # Show the traceback if the debug logging level is enabled
            exc_info_on_loglevel=logging.DEBUG
        )
        return {parallel_data['name']: {'Error': str(exc)}}

    if parallel_data['opts'].get('show_deploy_args', False) is False and isinstance(output, dict):
        output.pop('deploy_kwargs', None)

    return {
        parallel_data['name']: salt.utils.cloud.simple_types_filter(output)
    }