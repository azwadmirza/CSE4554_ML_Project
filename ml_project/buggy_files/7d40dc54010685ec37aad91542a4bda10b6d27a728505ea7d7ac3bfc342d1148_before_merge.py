def zone_exists(zone, region=None, key=None, keyid=None, profile=None,
                retry_on_rate_limit=None, rate_limit_retries=None,
                retry_on_errors=True, error_retries=5):
    '''
    Check for the existence of a Route53 hosted zone.

    .. versionadded:: 2015.8.0

    CLI Example::

        salt myminion boto_route53.zone_exists example.org
    '''
    if region is None:
        region = 'universal'

    conn = _get_conn(region=region, key=key, keyid=keyid, profile=profile)

    if retry_on_rate_limit or rate_limit_retries is not None:
        salt.utils.versions.warn_until(
            'Neon',
            'The \'retry_on_rate_limit\' and \'rate_limit_retries\' arguments '
            'have been deprecated in favor of \'retry_on_errors\' and '
            '\'error_retries\' respectively. Their functionality will be '
            'removed, as such, their usage is no longer required.'
        )
        if retry_on_rate_limit is not None:
            retry_on_errors = retry_on_rate_limit
        if rate_limit_retries is not None:
            error_retries = rate_limit_retries

    while error_retries > 0:
        try:
            return bool(conn.get_zone(zone))

        except DNSServerError as e:
            if retry_on_errors:
                if 'Throttling' == e.code:
                    log.debug('Throttled by AWS API.')
                elif 'PriorRequestNotComplete' == e.code:
                    log.debug('The request was rejected by AWS API.\
                              Route 53 was still processing a prior request')
                time.sleep(3)
                error_retries -= 1
                continue
            six.reraise(*sys.exc_info())