def delete_group_policy(group_name, policy_name, region=None, key=None,
                        keyid=None, profile=None):
    '''
    Delete a group policy.

    CLI Example::

    .. code-block:: bash

        salt myminion boto_iam.delete_group_policy mygroup mypolicy
    '''
    conn = _get_conn(region=region, key=key, keyid=keyid, profile=profile)
    if not conn:
        return False
    _policy = get_group_policy(
        group_name, policy_name, region, key, keyid, profile
    )
    if not _policy:
        return True
    try:
        conn.delete_group_policy(group_name, policy_name)
        msg = 'Successfully deleted {0} policy for group {1}.'
        log.info(msg.format(policy_name, group_name))
        return True
    except boto.exception.BotoServerError as e:
        log.debug(e)
        msg = 'Failed to delete {0} policy for group {1}.'
        log.error(msg.format(policy_name, group_name))
        return False