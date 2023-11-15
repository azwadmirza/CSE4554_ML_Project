def update_app(id, config):
    '''
    Update the specified app with the given configuration.

    CLI Example:
    .. code-block:: bash
        salt marathon-minion-id marathon.update_app my-app '<config yaml>'
    '''
    if 'id' not in config:
        config['id'] = id
    config.pop('version', None)
    data = json.dumps(config)
    try:
        response = salt.utils.http.query(
            "{0}/v2/apps/{1}?force=true".format(_base_url(), id),
            method='PUT',
            decode_type='json',
            decode=True,
            data=data,
            header_dict={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
        )
        log.debug('update response: %s', response)
        return response['dict']
    except Exception as ex:
        log.error('unable to update marathon app: %s', ex.message)
        return {
            'exception': {
                'message': ex.message,
            }
        }