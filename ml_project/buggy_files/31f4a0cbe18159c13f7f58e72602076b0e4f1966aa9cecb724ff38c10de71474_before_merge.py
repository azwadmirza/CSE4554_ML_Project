def sig4(method, endpoint, params, prov_dict,
         aws_api_version=DEFAULT_AWS_API_VERSION, location=None,
         product='ec2', uri='/', requesturl=None, data='', headers=None,
         role_arn=None, payload_hash=None):
    '''
    Sign a query against AWS services using Signature Version 4 Signing
    Process. This is documented at:

    http://docs.aws.amazon.com/general/latest/gr/sigv4_signing.html
    http://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html
    http://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html
    '''
    timenow = datetime.utcnow()

    # Retrieve access credentials from meta-data, or use provided
    if role_arn is None:
        access_key_id, secret_access_key, token = creds(prov_dict)
    else:
        access_key_id, secret_access_key, token = assumed_creds(prov_dict, role_arn, location=location)

    if location is None:
        location = get_region_from_metadata()
    if location is None:
        location = DEFAULT_LOCATION

    params_with_headers = params.copy()
    if product not in ('s3', 'ssm'):
        params_with_headers['Version'] = aws_api_version
    keys = sorted(params_with_headers.keys())
    values = list(map(params_with_headers.get, keys))
    querystring = urlencode(list(zip(keys, values))).replace('+', '%20')

    amzdate = timenow.strftime('%Y%m%dT%H%M%SZ')
    datestamp = timenow.strftime('%Y%m%d')
    new_headers = {}
    if isinstance(headers, dict):
        new_headers = headers.copy()

    # Create payload hash (hash of the request body content). For GET
    # requests, the payload is an empty string ('').
    if not payload_hash:
        payload_hash = hashlib.sha256(data).hexdigest()

    new_headers['X-Amz-date'] = amzdate
    new_headers['host'] = endpoint
    new_headers['x-amz-content-sha256'] = payload_hash
    a_canonical_headers = []
    a_signed_headers = []

    if token != '':
        new_headers['X-Amz-security-token'] = token

    for header in sorted(new_headers.keys(), key=str.lower):
        lower_header = header.lower()
        a_canonical_headers.append('{0}:{1}'.format(lower_header, new_headers[header].strip()))
        a_signed_headers.append(lower_header)
    canonical_headers = '\n'.join(a_canonical_headers) + '\n'
    signed_headers = ';'.join(a_signed_headers)

    algorithm = 'AWS4-HMAC-SHA256'

    # Combine elements to create create canonical request
    canonical_request = '\n'.join((
        method,
        uri,
        querystring,
        canonical_headers,
        signed_headers,
        payload_hash
    ))

    # Create the string to sign
    credential_scope = '/'.join((datestamp, location, product, 'aws4_request'))
    string_to_sign = '\n'.join((
        algorithm,
        amzdate,
        credential_scope,
        hashlib.sha256(canonical_request).hexdigest()
    ))

    # Create the signing key using the function defined above.
    signing_key = _sig_key(
        secret_access_key,
        datestamp,
        location,
        product
    )

    # Sign the string_to_sign using the signing_key
    signature = hmac.new(
        signing_key,
        string_to_sign.encode('utf-8'),
        hashlib.sha256).hexdigest()

    # Add signing information to the request
    authorization_header = (
            '{0} Credential={1}/{2}, SignedHeaders={3}, Signature={4}'
        ).format(
            algorithm,
            access_key_id,
            credential_scope,
            signed_headers,
            signature,
        )

    new_headers['Authorization'] = authorization_header

    requesturl = '{0}?{1}'.format(requesturl, querystring)
    return new_headers, requesturl