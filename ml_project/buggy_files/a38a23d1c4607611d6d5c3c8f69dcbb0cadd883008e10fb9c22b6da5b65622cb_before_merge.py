def query(params=None, setname=None, requesturl=None, location=None,
          return_url=False, return_root=False):

    provider = get_configured_provider()
    service_url = provider.get('service_url', 'amazonaws.com')

    # Retrieve access credentials from meta-data, or use provided
    access_key_id, secret_access_key, token = aws.creds(provider)

    attempts = 5
    while attempts > 0:
        params_with_headers = params.copy()
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        if not location:
            location = get_location()

        if not requesturl:
            endpoint = provider.get(
                'endpoint',
                'ec2.{0}.{1}'.format(location, service_url)
            )

            requesturl = 'https://{0}/'.format(endpoint)
            endpoint = _urlparse(requesturl).netloc
            endpoint_path = _urlparse(requesturl).path
        else:
            endpoint = _urlparse(requesturl).netloc
            endpoint_path = _urlparse(requesturl).path
            if endpoint == '':
                endpoint_err = (
                        'Could not find a valid endpoint in the '
                        'requesturl: {0}. Looking for something '
                        'like https://some.ec2.endpoint/?args').format(requesturl)
                log.error(endpoint_err)
                if return_url is True:
                    return {'error': endpoint_err}, requesturl
                return {'error': endpoint_err}

        log.debug('Using EC2 endpoint: {0}'.format(endpoint))
        # AWS v4 signature

        method = 'GET'
        region = location
        service = 'ec2'
        canonical_uri = _urlparse(requesturl).path
        host = endpoint.strip()

        # Create a date for headers and the credential string
        t = datetime.datetime.utcnow()
        amz_date = t.strftime('%Y%m%dT%H%M%SZ')  # Format date as YYYYMMDD'T'HHMMSS'Z'
        datestamp = t.strftime('%Y%m%d')  # Date w/o time, used in credential scope

        canonical_headers = 'host:' + host + '\n' + 'x-amz-date:' + amz_date + '\n'
        signed_headers = 'host;x-amz-date'

        payload_hash = hashlib.sha256('').hexdigest()

        ec2_api_version = provider.get(
            'ec2_api_version',
            DEFAULT_EC2_API_VERSION
        )

        params_with_headers['Version'] = ec2_api_version

        keys = sorted(params_with_headers.keys())
        values = map(params_with_headers.get, keys)
        querystring = _urlencode(list(zip(keys, values)))
        querystring = querystring.replace('+', '%20')

        canonical_request = method + '\n' + canonical_uri + '\n' + \
                    querystring + '\n' + canonical_headers + '\n' + \
                    signed_headers + '\n' + payload_hash

        algorithm = 'AWS4-HMAC-SHA256'
        credential_scope = datestamp + '/' + region + '/' + service + '/' + 'aws4_request'

        string_to_sign = algorithm + '\n' +  amz_date + '\n' + \
                         credential_scope + '\n' + \
                         hashlib.sha256(canonical_request).hexdigest()

        kDate = sign(('AWS4' + provider['key']).encode('utf-8'), datestamp)
        kRegion = sign(kDate, region)
        kService = sign(kRegion, service)
        signing_key = sign(kService, 'aws4_request')

        signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'),
                             hashlib.sha256).hexdigest()
        #sig = binascii.b2a_base64(hashed)

        authorization_header = algorithm + ' ' + 'Credential=' + \
                               provider['id'] + '/' + credential_scope + \
                               ', ' +  'SignedHeaders=' + signed_headers + \
                               ', ' + 'Signature=' + signature
        headers = {'x-amz-date': amz_date, 'Authorization': authorization_header}

        log.debug('EC2 Request: {0}'.format(requesturl))
        log.trace('EC2 Request Parameters: {0}'.format(params_with_headers))
        try:
            result = requests.get(requesturl, headers=headers, params=params_with_headers)
            log.debug(
                'EC2 Response Status Code: {0}'.format(
                    # result.getcode()
                    result.status_code
                )
            )
            log.trace(
                'EC2 Response Text: {0}'.format(
                    result.text
                )
            )
            result.raise_for_status()
            break
        except requests.exceptions.HTTPError as exc:
            root = ET.fromstring(exc.response.content)
            data = _xml_to_dict(root)

            # check to see if we should retry the query
            err_code = data.get('Errors', {}).get('Error', {}).get('Code', '')
            if attempts > 0 and err_code and err_code in EC2_RETRY_CODES:
                attempts -= 1
                log.error(
                    'EC2 Response Status Code and Error: [{0} {1}] {2}; '
                    'Attempts remaining: {3}'.format(
                        exc.response.status_code, exc, data, attempts
                    )
                )
                # Wait a bit before continuing to prevent throttling
                time.sleep(2)
                continue

            log.error(
                'EC2 Response Status Code and Error: [{0} {1}] {2}'.format(
                    exc.response.status_code, exc, data
                )
            )
            if return_url is True:
                return {'error': data}, requesturl
            return {'error': data}
    else:
        log.error(
            'EC2 Response Status Code and Error: [{0} {1}] {2}'.format(
                exc.response.status_code, exc, data
            )
        )
        if return_url is True:
            return {'error': data}, requesturl
        return {'error': data}

    response = result.text

    root = ET.fromstring(response)
    items = root[1]
    if return_root is True:
        items = root

    if setname:
        if sys.version_info < (2, 7):
            children_len = len(root.getchildren())
        else:
            children_len = len(root)

        for item in range(0, children_len):
            comps = root[item].tag.split('}')
            if comps[1] == setname:
                items = root[item]

    ret = []
    for item in items:
        ret.append(_xml_to_dict(item))

    if return_url is True:
        return ret, requesturl

    return ret