def update_job(name, config):
    '''
    Update the specified job with the given configuration.

    CLI Example:
    .. code-block:: bash
        salt chronos-minion-id chronos.update_job my-job '<config yaml>'
    '''
    if 'name' not in config:
        config['name'] = name
    data = json.dumps(config)
    try:
        response = salt.utils.http.query(
            "{0}/scheduler/iso8601".format(_base_url()),
            method='POST',
            data=data,
            header_dict={
                'Content-Type': 'application/json',
            },
        )
        log.debug('update response: %s', response)
        return {'success': True}
    except Exception as ex:
        log.error('unable to update chronos job: %s', ex.message)
        return {
            'exception': {
                'message': ex.message,
            }
        }