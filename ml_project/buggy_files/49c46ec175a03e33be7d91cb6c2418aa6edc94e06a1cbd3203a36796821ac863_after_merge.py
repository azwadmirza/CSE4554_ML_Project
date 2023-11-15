def query(params=None):
    '''
    Make a web call to aliyun ECS REST API
    '''
    path = 'https://ecs-cn-hangzhou.aliyuncs.com'

    access_key_id = config.get_cloud_config_value(
        'id', get_configured_provider(), __opts__, search_global=False
    )
    access_key_secret = config.get_cloud_config_value(
        'key', get_configured_provider(), __opts__, search_global=False
    )

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # public interface parameters
    parameters = {
        'Format': 'JSON',
        'Version': DEFAULT_ALIYUN_API_VERSION,
        'AccessKeyId': access_key_id,
        'SignatureVersion': '1.0',
        'SignatureMethod': 'HMAC-SHA1',
        'SignatureNonce': six.text_type(uuid.uuid1()),
        'TimeStamp': timestamp,
    }

    # include action or function parameters
    if params:
        parameters.update(params)

    # Calculate the string for Signature
    signature = _compute_signature(parameters, access_key_secret)
    parameters['Signature'] = signature

    request = requests.get(path, params=parameters, verify=True)
    if request.status_code != 200:
        raise SaltCloudSystemExit(
            'An error occurred while querying aliyun ECS. HTTP Code: {0}  '
            'Error: \'{1}\''.format(
                request.status_code,
                request.text
            )
        )

    log.debug(request.url)

    content = request.text

    result = salt.utils.json.loads(content)
    if 'Code' in result:
        raise SaltCloudSystemExit(
            pprint.pformat(result.get('Message', {}))
        )
    return result