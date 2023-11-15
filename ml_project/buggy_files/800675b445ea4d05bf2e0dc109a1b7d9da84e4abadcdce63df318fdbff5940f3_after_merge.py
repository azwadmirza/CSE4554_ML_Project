def _query(path, method='GET', data=None, params=None, header_dict=None, decode=True):
    '''
    Perform a query directly against the Vultr REST API
    '''
    api_key = config.get_cloud_config_value(
        'api_key',
        get_configured_provider(),
        __opts__,
        search_global=False,
    )
    management_host = config.get_cloud_config_value(
        'management_host',
        get_configured_provider(),
        __opts__,
        search_global=False,
        default='api.vultr.com'
    )
    url = 'https://{management_host}/v1/{path}?api_key={api_key}'.format(
        management_host=management_host,
        path=path,
        api_key=api_key,
    )

    if header_dict is None:
        header_dict = {}

    result = __utils__['http.query'](
        url,
        method=method,
        params=params,
        data=data,
        header_dict=header_dict,
        port=443,
        text=True,
        decode=decode,
        decode_type='json',
        hide_fields=['api_key'],
        opts=__opts__,
    )
    if 'dict' in result:
        return result['dict']

    return result