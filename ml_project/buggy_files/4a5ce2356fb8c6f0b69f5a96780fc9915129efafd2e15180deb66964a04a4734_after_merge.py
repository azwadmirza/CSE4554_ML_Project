def put_group_policy(group_name, policy_name, policy_json, region=None, key=None,
                     keyid=None, profile=None):
    '''
    Adds or updates the specified policy document for the specified group.

    .. versionadded:: 2015.8.0

    CLI Example:

    .. code-block:: bash

        salt myminion boto_iam.put_group_policy mygroup policyname policyrules
    '''
    group = get_group(group_name, region=region, key=key, keyid=keyid, profile=profile)
    if not group:
        log.error('Group {0} does not exist'.format(group_name))
        return False
    conn = _get_conn(region=region, key=key, keyid=keyid, profile=profile)
    try:
        if not isinstance(policy_json, string_types):
            policy_json = json.dumps(policy_json)
        created = conn.put_group_policy(group_name, policy_name,
                                        policy_json)
        if created:
            log.info('Created policy for group {0}.'.format(group_name))
            return True
        msg = 'Could not create policy for group {0}'
        log.error(msg.format(group_name))
    except boto.exception.BotoServerError as e:
        log.debug(e)
        msg = 'Failed to create policy for group {0}'
        log.error(msg.format(group_name))
    return False