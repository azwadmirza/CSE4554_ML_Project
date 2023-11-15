def _compute_diff(configured, expected):

    '''Computes the differences between the actual config and the expected config'''

    diff = {
        'add': {},
        'update': {},
        'remove': {}
    }

    configured_users = set(configured.keys())
    expected_users = set(expected.keys())

    add_usernames = expected_users - configured_users
    remove_usernames = configured_users - expected_users
    common_usernames = expected_users & configured_users

    add = dict((username, expected.get(username)) for username in add_usernames)
    remove = dict((username, configured.get(username)) for username in remove_usernames)
    update = {}

    for username in common_usernames:
        user_configuration = configured.get(username)
        user_expected = expected.get(username)
        if user_configuration == user_expected:
            continue
        update[username] = {}
        for field, field_value in six.iteritems(user_expected):
            if user_configuration.get(field) != field_value:
                update[username][field] = field_value

    diff.update({
        'add': add,
        'update': update,
        'remove': remove
    })

    return diff