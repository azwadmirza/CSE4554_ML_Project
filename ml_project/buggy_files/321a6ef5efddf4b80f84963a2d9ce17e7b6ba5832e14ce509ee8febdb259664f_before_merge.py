def get_all_group_policies(group_name, region=None, key=None, keyid=None,
                           profile=None):
    '''
    Get a list of policy names from a group.

    CLI Example:

    .. code-block:: bash

        salt myminion boto_iam.get_all_group_policies mygroup
    '''
    conn = _get_conn(region, key, keyid, profile)
    if not conn:
        return False
    try:
        response = conn.get_all_group_policies(group_name)
        _list = response.list_group_policies_response.list_group_policies_result
        return _list.policy_names
    except boto.exception.BotoServerError as e:
        log.debug(e)
        return []