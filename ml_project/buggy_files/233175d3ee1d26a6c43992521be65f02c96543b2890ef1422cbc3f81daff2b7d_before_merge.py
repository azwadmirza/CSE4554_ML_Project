def create_healthcheck(ip_addr=None, fqdn=None, region=None, key=None, keyid=None, profile=None,
                      port=53, hc_type='TCP', resource_path='', string_match=None, request_interval=30,
                      failure_threshold=3, retry_on_errors=True, error_retries=5):
    '''
    Create a Route53 healthcheck

    .. versionadded:: 2018.3.0

    ip_addr

        IP address to check.  ip_addr or fqdn is required.

    fqdn

        Domain name of the endpoint to check.  ip_addr or fqdn is required

    port

        Port to check

    hc_type

        Healthcheck type.  HTTP | HTTPS | HTTP_STR_MATCH | HTTPS_STR_MATCH | TCP

    resource_path

        Path to check

    string_match

        If hc_type is HTTP_STR_MATCH or HTTPS_STR_MATCH, the string to search for in the
        response body from the specified resource

    request_interval

        The number of seconds between the time that Amazon Route 53 gets a response from
        your endpoint and the time that it sends the next health-check request.

    failure_threshold

        The number of consecutive health checks that an endpoint must pass or fail for
        Amazon Route 53 to change the current status of the endpoint from unhealthy to
        healthy or vice versa.

    region

        Region endpoint to connect to

    key

        AWS key

    keyid

        AWS keyid

    profile

        AWS pillar profile

    CLI Example::

        salt myminion boto_route53.create_healthcheck 192.168.0.1
        salt myminion boto_route53.create_healthcheck 192.168.0.1 port=443 hc_type=HTTPS \
                                                      resource_path=/ fqdn=blog.saltstack.furniture
    '''
    if fqdn is None and ip_addr is None:
        msg = 'One of the following must be specified: fqdn or ip_addr'
        log.error(msg)
        return {'error': msg}
    hc_ = boto.route53.healthcheck.HealthCheck(ip_addr,
                                               port,
                                               hc_type,
                                               resource_path,
                                               fqdn=fqdn,
                                               string_match=string_match,
                                               request_interval=request_interval,
                                               failure_threshold=failure_threshold)

    if region is None:
        region = 'universal'

    conn = _get_conn(region=region, key=key, keyid=keyid, profile=profile)

    while error_retries > 0:
        try:
            return {'result': conn.create_health_check(hc_)}
        except DNSServerError as exc:
            log.debug(exc)
            if retry_on_errors:
                if 'Throttling' == exc.code:
                    log.debug('Throttled by AWS API.')
                elif 'PriorRequestNotComplete' == exc.code:
                    log.debug('The request was rejected by AWS API.\
                              Route 53 was still processing a prior request')
                time.sleep(3)
                error_retries -= 1
                continue
            return {'error': __utils__['boto.get_error'](exc)}
    return False