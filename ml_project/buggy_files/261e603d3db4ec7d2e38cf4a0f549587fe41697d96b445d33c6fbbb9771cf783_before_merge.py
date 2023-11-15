def delete_subnet_group(name, region=None, key=None, keyid=None, profile=None):
    '''
    Delete an ElastiCache subnet group.

    CLI example::

        salt myminion boto_elasticache.delete_subnet_group my-subnet-group \
                region=us-east-1
    '''
    conn = _get_conn(region, key, keyid, profile)
    if not conn:
        return False
    try:
        conn.delete_cache_subnet_group(name)
        msg = 'Deleted ElastiCache subnet group {0}.'.format(name)
        log.info(msg)
        return True
    except boto.exception.BotoServerError as e:
        log.debug(e)
        msg = 'Failed to delete ElastiCache subnet group {0}'.format(name)
        log.error(msg)
        return False