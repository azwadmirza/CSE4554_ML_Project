def creds(provider):
    '''
    Return the credentials for AWS signing.  This could be just the id and key
    specified in the provider configuration, or if the id or key is set to the
    literal string 'use-instance-role-credentials' creds will pull the instance
    role credentials from the meta data, cache them, and provide them instead.
    '''
    # Declare globals
    global __AccessKeyId__, __SecretAccessKey__, __Token__, __Expiration__

    # if id or key is 'use-instance-role-credentials', pull them from meta-data
    ## if needed
    if provider['id'] == IROLE_CODE or provider['key'] == IROLE_CODE:
        # Check to see if we have cache credentials that are still good
        if __Expiration__ != '':
            timenow = datetime.utcnow()
            timestamp = timenow.strftime('%Y-%m-%dT%H:%M:%SZ')
            if timestamp < __Expiration__:
                # Current timestamp less than expiration fo cached credentials
                return __AccessKeyId__, __SecretAccessKey__, __Token__
        # We don't have any cached credentials, or they are expired, get them

        # Connections to instance meta-data must fail fast and never be proxied
        try:
            result = requests.get(
                "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
                proxies={'http': ''}, timeout=AWS_METADATA_TIMEOUT,
            )
            result.raise_for_status()
            role = result.text.encode(result.encoding)
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
            return provider['id'], provider['key'], ''

        try:
            result = requests.get(
                "http://169.254.169.254/latest/meta-data/iam/security-credentials/{0}".format(role),
                proxies={'http': ''}, timeout=AWS_METADATA_TIMEOUT,
            )
            result.raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
            return provider['id'], provider['key'], ''

        data = result.json()
        __AccessKeyId__ = data['AccessKeyId']
        __SecretAccessKey__ = data['SecretAccessKey']
        __Token__ = data['Token']
        __Expiration__ = data['Expiration']
        return __AccessKeyId__, __SecretAccessKey__, __Token__
    else:
        return provider['id'], provider['key'], ''