def delete_record(name, zone, record_type, identifier=None, all_records=False,
                  region=None, key=None, keyid=None, profile=None,
                  wait_for_sync=True, split_dns=False, private_zone=False,
                  retry_on_rate_limit=None, rate_limit_retries=None,
                  retry_on_errors=True, error_retries=5):
    '''
    Modify a record in a zone.

    CLI example::

        salt myminion boto_route53.delete_record test.example.org example.org A
    '''
    if region is None:
        region = 'universal'

    conn = _get_conn(region=region, key=key, keyid=keyid, profile=profile)

    if split_dns:
        _zone = _get_split_zone(zone, conn, private_zone)
    else:
        _zone = conn.get_zone(zone)
    if not _zone:
        msg = 'Failed to retrieve zone {0}'.format(zone)
        log.error(msg)
        return False
    _type = record_type.upper()

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
            old_record = _zone.find_records(name, _type, all=all_records, identifier=identifier)
            if not old_record:
                return False
            status = _zone.delete_record(old_record)
            return _wait_for_sync(status.id, conn, wait_for_sync)

        except DNSServerError as e:
            if retry_on_errors and _is_retryable_error(e):
                if 'Throttling' == e.code:
                    log.debug('Throttled by AWS API.')
                elif 'PriorRequestNotComplete' == e.code:
                    log.debug('The request was rejected by AWS API.\
                              Route 53 was still processing a prior request')
                time.sleep(3)
                error_retries -= 1
                continue
            six.reraise(*sys.exc_info())