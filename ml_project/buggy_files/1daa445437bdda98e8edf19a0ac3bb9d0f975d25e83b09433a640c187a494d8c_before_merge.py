def add_record(name, value, zone, record_type, identifier=None, ttl=None,
               region=None, key=None, keyid=None, profile=None,
               wait_for_sync=True, split_dns=False, private_zone=False,
               retry_on_rate_limit=True, rate_limit_retries=5):
    '''
    Add a record to a zone.

    CLI example::

        salt myminion boto_route53.add_record test.example.org 1.1.1.1 example.org A
    '''
    if region is None:
        region = 'universal'

    conn = _get_conn(region=region, key=key, keyid=keyid, profile=profile)

    while rate_limit_retries > 0:
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
            # if rate limit, retry:
            if retry_on_rate_limit and 'Throttling' == e.code:
                log.debug('Throttled by AWS API.')
                time.sleep(2)
                rate_limit_retries -= 1
                continue  # the while True; try again if not out of retries
            raise e

    _value = _munge_value(value, _type)
    while rate_limit_retries > 0:
        try:
            if _type == 'A':
                status = _zone.add_a(name, _value, ttl, identifier)
                return _wait_for_sync(status.id, conn, wait_for_sync)
            elif _type == 'CNAME':
                status = _zone.add_cname(name, _value, ttl, identifier)
                return _wait_for_sync(status.id, conn, wait_for_sync)
            elif _type == 'MX':
                status = _zone.add_mx(name, _value, ttl, identifier)
                return _wait_for_sync(status.id, conn, wait_for_sync)
            else:
                # add_record requires a ttl value, annoyingly.
                if ttl is None:
                    ttl = 60
                status = _zone.add_record(_type, name, _value, ttl, identifier)
                return _wait_for_sync(status.id, conn, wait_for_sync)

        except DNSServerError as e:
            # if rate limit, retry:
            if retry_on_rate_limit and 'Throttling' == e.code:
                log.debug('Throttled by AWS API.')
                time.sleep(2)
                rate_limit_retries -= 1
                continue  # the while True; try again if not out of retries
            raise e