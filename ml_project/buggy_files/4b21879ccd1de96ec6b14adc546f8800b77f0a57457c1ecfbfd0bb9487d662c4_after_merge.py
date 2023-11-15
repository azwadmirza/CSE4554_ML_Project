def delete(name, skip_final_snapshot=None, final_db_snapshot_identifier=None,
           region=None, key=None, keyid=None, profile=None):
    '''
    Delete an RDS instance.

    CLI example::

        salt myminion boto_rds.delete myrds skip_final_snapshot=True \
                region=us-east-1
    '''
    conn = _get_conn(region=region, key=key, keyid=keyid, profile=profile)

    if not skip_final_snapshot and not final_db_snapshot_identifier:
        raise SaltInvocationError('At least on of the following must'
                                  ' be specified: skip_final_snapshot'
                                  ' final_db_snapshot_identifier')
    try:
        conn.delete_db_instance(name, skip_final_snapshot,
                                final_db_snapshot_identifier)
        msg = 'Deleted RDS instance {0}.'.format(name)
        log.info(msg)
        return True
    except boto.exception.BotoServerError as e:
        log.debug(e)
        msg = 'Failed to delete RDS instance {0}'.format(name)
        log.error(msg)
        return False