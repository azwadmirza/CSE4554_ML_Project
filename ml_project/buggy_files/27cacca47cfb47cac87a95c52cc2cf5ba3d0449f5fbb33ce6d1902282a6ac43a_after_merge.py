def query(params=None):
    '''
    Make a web call to QingCloud IaaS API.
    '''
    path = 'https://api.qingcloud.com/iaas/'

    access_key_id = config.get_cloud_config_value(
        'access_key_id', get_configured_provider(), __opts__, search_global=False
    )
    access_key_secret = config.get_cloud_config_value(
        'secret_access_key', get_configured_provider(), __opts__, search_global=False
    )

    # public interface parameters
    real_parameters = {
        'access_key_id': access_key_id,
        'signature_version': DEFAULT_QINGCLOUD_SIGNATURE_VERSION,
        'time_stamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'version': DEFAULT_QINGCLOUD_API_VERSION,
    }

    # include action or function parameters
    if params:
        for key, value in params.items():
            if isinstance(value, list):
                for i in range(1, len(value) + 1):
                    if isinstance(value[i - 1], dict):
                        for sk, sv in value[i - 1].items():
                            if isinstance(sv, dict) or isinstance(sv, list):
                                sv = salt.utils.json.dumps(sv, separators=(',', ':'))
                            real_parameters['{0}.{1}.{2}'.format(key, i, sk)] = sv
                    else:
                        real_parameters['{0}.{1}'.format(key, i)] = value[i - 1]
            else:
                real_parameters[key] = value

    # Calculate the string for Signature
    signature = _compute_signature(real_parameters, access_key_secret, 'GET', '/iaas/')
    real_parameters['signature'] = signature

    # print('parameters:')
    # pprint.pprint(real_parameters)

    request = requests.get(path, params=real_parameters, verify=False)

    # print('url:')
    # print(request.url)

    if request.status_code != 200:
        raise SaltCloudSystemExit(
            'An error occurred while querying QingCloud. HTTP Code: {0}  '
            'Error: \'{1}\''.format(
                request.status_code,
                request.text
            )
        )

    log.debug(request.url)

    content = request.text
    result = salt.utils.json.loads(content)

    # print('response:')
    # pprint.pprint(result)

    if result['ret_code'] != 0:
        raise SaltCloudSystemExit(
            pprint.pformat(result.get('message', {}))
        )

    return result