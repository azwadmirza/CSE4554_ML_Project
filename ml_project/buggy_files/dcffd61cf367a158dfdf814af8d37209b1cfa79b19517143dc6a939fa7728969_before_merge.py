def create_subnet_group(name, description, subnet_ids, tags=None, region=None,
                        key=None, keyid=None, profile=None):
    '''
    Create an ElastiCache subnet group

    CLI example to create an ElastiCache subnet group::

        salt myminion boto_elasticache.create_subnet_group my-subnet-group \
            "group description" '[subnet-12345678, subnet-87654321]' \
            region=us-east-1
    '''
    conn = _get_conn(region, key, keyid, profile)
    if not conn:
        return False
    if subnet_group_exists(name, tags, region, key, keyid, profile):
        return True
    try:
        ec = conn.create_cache_subnet_group(name, description, subnet_ids)
        if not ec:
            msg = 'Failed to create ElastiCache subnet group {0}'.format(name)
            log.error(msg)
            return False
        log.info('Created ElastiCache subnet group {0}'.format(name))
        return True
    except boto.exception.BotoServerError as e:
        log.debug(e)
        msg = 'Failed to create ElastiCache subnet group {0}'.format(name)
        log.error(msg)
        return False