def put_user_policy(user_name, policy_name, policy_json, region=None, key=None, keyid=None, profile=None):
    '''
    Adds or updates the specified policy document for the specified user.

    .. versionadded:: 2015.8.0

    CLI Example:

    .. code-block:: bash

        salt myminion boto_iam.put_user_policy myuser policyname policyrules
    '''
    user = get_user(user_name, region, key, keyid, profile)
    if not user:
        log.error('User {0} does not exist'.format(user_name))
        return False
    conn = _get_conn(region=region, key=key, keyid=keyid, profile=profile)
    try:
        if not isinstance(policy_json, string_types):
            policy_json = json.dumps(policy_json)
        created = conn.put_user_policy(user_name, policy_name,
                                       policy_json)
        if created:
            log.info('Created policy for user {0}.'.format(user_name))
            return True
        msg = 'Could not create policy for user {0}.'
        log.error(msg.format(user_name))
    except boto.exception.BotoServerError as e:
        log.debug(e)
        msg = 'Failed to create policy for user {0}.'
        log.error(msg.format(user_name))
    return False