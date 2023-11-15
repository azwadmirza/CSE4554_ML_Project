def query(params=None, setname=None, requesturl=None, location=None,
          return_url=False, return_root=False, opts=None, provider=None,
          endpoint=None, product='ec2', sigver='2'):
    '''
    Perform a query against AWS services using Signature Version 2 Signing
    Process. This is documented at:

    http://docs.aws.amazon.com/general/latest/gr/signature-version-2.html

    Regions and endpoints are documented at:

    http://docs.aws.amazon.com/general/latest/gr/rande.html

    Default ``product`` is ``ec2``. Valid ``product`` names are:

    .. code-block: yaml

        - autoscaling (Auto Scaling)
        - cloudformation (CloudFormation)
        - ec2 (Elastic Compute Cloud)
        - elasticache (ElastiCache)
        - elasticbeanstalk (Elastic BeanStalk)
        - elasticloadbalancing (Elastic Load Balancing)
        - elasticmapreduce (Elastic MapReduce)
        - iam (Identity and Access Management)
        - importexport (Import/Export)
        - monitoring (CloudWatch)
        - rds (Relational Database Service)
        - simpledb (SimpleDB)
        - sns (Simple Notification Service)
        - sqs (Simple Queue Service)
    '''
    if params is None:
        params = {}

    if opts is None:
        opts = {}

    function = opts.get('function', (None, product))
    providers = opts.get('providers', {})

    if provider is None:
        prov_dict = providers.get(function[1], {}).get(product, {})
        if prov_dict:
            driver = list(list(prov_dict.keys()))[0]
            provider = providers.get(driver, product)
    else:
        prov_dict = providers.get(provider, {}).get(product, {})

    service_url = prov_dict.get('service_url', 'amazonaws.com')

    if not location:
        location = get_location(opts, provider)

    if endpoint is None:
        if not requesturl:
            endpoint = prov_dict.get(
                'endpoint',
                '{0}.{1}.{2}'.format(product, location, service_url)
            )

            requesturl = 'https://{0}/'.format(endpoint)
        else:
            endpoint = urlparse(requesturl).netloc
            if endpoint == '':
                endpoint_err = ('Could not find a valid endpoint in the '
                                'requesturl: {0}. Looking for something '
                                'like https://some.aws.endpoint/?args').format(
                                    requesturl
                                )
                LOG.error(endpoint_err)
                if return_url is True:
                    return {'error': endpoint_err}, requesturl
                return {'error': endpoint_err}

    LOG.debug('Using AWS endpoint: {0}'.format(endpoint))
    method = 'GET'

    aws_api_version = prov_dict.get(
        'aws_api_version', prov_dict.get(
            '{0}_api_version'.format(product),
            DEFAULT_AWS_API_VERSION
        )
    )

    # Fallback to ec2's id & key if none is found, for this component
    if not prov_dict.get('id', None):
        prov_dict['id'] = providers.get(provider, {}).get('ec2', {}).get('id', {})
        prov_dict['key'] = providers.get(provider, {}).get('ec2', {}).get('key', {})

    if sigver == '4':
        headers, requesturl = sig4(
            method, endpoint, params, prov_dict, aws_api_version, location, product, requesturl=requesturl
        )
        params_with_headers = {}
    else:
        params_with_headers = sig2(
            method, endpoint, params, prov_dict, aws_api_version
        )
        headers = {}

    attempts = 5
    while attempts > 0:
        LOG.debug('AWS Request: {0}'.format(requesturl))
        LOG.trace('AWS Request Parameters: {0}'.format(params_with_headers))
        try:
            result = requests.get(requesturl, headers=headers, params=params_with_headers)
            LOG.debug(
                'AWS Response Status Code: {0}'.format(
                    result.status_code
                )
            )
            LOG.trace(
                'AWS Response Text: {0}'.format(
                    result.text
                )
            )
            result.raise_for_status()
            break
        except requests.exceptions.HTTPError as exc:
            root = ET.fromstring(exc.response.content)
            data = xml.to_dict(root)

            # check to see if we should retry the query
            err_code = data.get('Errors', {}).get('Error', {}).get('Code', '')
            if attempts > 0 and err_code and err_code in AWS_RETRY_CODES:
                attempts -= 1
                LOG.error(
                    'AWS Response Status Code and Error: [{0} {1}] {2}; '
                    'Attempts remaining: {3}'.format(
                        exc.response.status_code, exc, data, attempts
                    )
                )
                # Wait a bit before continuing to prevent throttling
                time.sleep(2)
                continue

            LOG.error(
                'AWS Response Status Code and Error: [{0} {1}] {2}'.format(
                    exc.response.status_code, exc, data
                )
            )
            if return_url is True:
                return {'error': data}, requesturl
            return {'error': data}
    else:
        LOG.error(
            'AWS Response Status Code and Error: [{0} {1}] {2}'.format(
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
        ret.append(xml.to_dict(item))

    if return_url is True:
        return ret, requesturl

    return ret