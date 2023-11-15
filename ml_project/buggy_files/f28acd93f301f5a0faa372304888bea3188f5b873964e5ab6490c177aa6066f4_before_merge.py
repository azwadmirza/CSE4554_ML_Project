def delete_user_policy(user_name, policy_name, region=None, key=None, keyid=None, profile=None):
    '''
    Delete a user policy.

    CLI Example:

    .. code-block:: bash

        salt myminion boto_iam.delete_user_policy myuser mypolicy
    '''
    conn = _get_conn(region, key, keyid, profile)
    if not conn:
        return False
    _policy = get_user_policy(
        user_name, policy_name, region, key, keyid, profile
    )
    if not _policy:
        return True
    try:
        conn.delete_user_policy(user_name, policy_name)
        msg = 'Successfully deleted {0} policy for user {1}.'
        log.info(msg.format(policy_name, user_name))
        return True
    except boto.exception.BotoServerError as e:
        log.debug(e)
        msg = 'Failed to delete {0} policy for user {1}.'
        log.error(msg.format(policy_name, user_name))
        return False