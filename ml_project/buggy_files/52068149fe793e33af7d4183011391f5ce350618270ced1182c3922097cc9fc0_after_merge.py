def subnet_group_exists(name, tags=None, region=None, key=None, keyid=None, profile=None):
    '''
    Check to see if an ElastiCache subnet group exists.

    CLI example::

        salt myminion boto_elasticache.subnet_group_exists my-param-group \
                region=us-east-1
    '''
    conn = _get_conn(region=region, key=key, keyid=keyid, profile=profile)
    if not conn:
        return False
    try:
        ec = conn.describe_cache_subnet_groups(cache_subnet_group_name=name)
        if not ec:
            msg = ('ElastiCache subnet group does not exist in region {0}'.format(region))
            log.debug(msg)
            return False
        return True
    except boto.exception.BotoServerError as e:
        log.debug(e)
        return False