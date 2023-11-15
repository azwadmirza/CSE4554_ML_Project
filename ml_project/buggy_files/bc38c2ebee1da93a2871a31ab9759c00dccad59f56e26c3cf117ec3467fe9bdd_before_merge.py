def delete_record(name, zone, record_type, identifier=None, all_records=False,
                  region=None, key=None, keyid=None, profile=None,
                  wait_for_sync=True, split_dns=False, private_zone=False,
                  retry_on_rate_limit=True, rate_limit_retries=5):
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

    while rate_limit_retries > 0:
        try:
            if _type == 'A':
                status = _zone.delete_a(name, identifier, all_records)
                return _wait_for_sync(status.id, conn, wait_for_sync)
            elif _type == 'CNAME':
                status = _zone.delete_cname(name, identifier, all_records)
                return _wait_for_sync(status.id, conn, wait_for_sync)
            elif _type == 'MX':
                status = _zone.delete_mx(name, identifier, all_records)
                return _wait_for_sync(status.id, conn, wait_for_sync)
            else:
                old_record = _zone.find_records(name, _type, all=all_records)
                if not old_record:
                    return False
                status = _zone.delete_record(old_record)
                return _wait_for_sync(status.id, conn, wait_for_sync)

        except DNSServerError as e:
            # if rate limit, retry:
            if retry_on_rate_limit and 'Throttling' == e.code:
                log.debug('Throttled by AWS API.')
                time.sleep(2)
                rate_limit_retries -= 1
                continue  # the while True; try again if not out of retries
            raise e