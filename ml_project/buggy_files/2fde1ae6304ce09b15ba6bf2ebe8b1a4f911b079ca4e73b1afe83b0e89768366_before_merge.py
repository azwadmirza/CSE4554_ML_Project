def add_record(name, value, zone, record_type, identifier=None, ttl=None,
               region=None, key=None, keyid=None, profile=None,
               wait_for_sync=True, split_dns=False, private_zone=False,
               retry_on_rate_limit=None, rate_limit_retries=None,
               retry_on_errors=True, error_retries=5):
    '''
    Add a record to a zone.

    CLI example::

        salt myminion boto_route53.add_record test.example.org 1.1.1.1 example.org A
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
            if split_dns:
                _zone = _get_split_zone(zone, conn, private_zone)
            else:
                _zone = conn.get_zone(zone)
            if not _zone:
                msg = 'Failed to retrieve zone {0}'.format(zone)
                log.error(msg)
                return False
            _type = record_type.upper()
            break

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

    _value = _munge_value(value, _type)
    while error_retries > 0:
        try:
            # add_record requires a ttl value, annoyingly.
            if ttl is None:
                ttl = 60
            status = _zone.add_record(_type, name, _value, ttl, identifier)
            return _wait_for_sync(status.id, conn, wait_for_sync)

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