def check_perms(path,
                ret=None,
                owner=None,
                grant_perms=None,
                deny_perms=None,
                inheritance=True):
    '''
    Set owner and permissions for each directory created.

    Args:

        path (str): The full path to the directory.

        ret (dict): A dictionary to append changes to and return. If not passed,
        will create a new dictionary to return.

        owner (str): The owner of the directory. If not passed, it will be the
        account that created the directory, likely SYSTEM

        grant_perms (dict): A dictionary containing the user/group and the basic
        permissions to grant, ie: ``{'user': {'perms': 'basic_permission'}}``.
        You can also set the ``applies_to`` setting here. The default is
        ``this_folder_subfolders_files``. Specify another ``applies_to`` setting
        like this:

        .. code-block:: yaml

            {'user': {'perms': 'full_control', 'applies_to': 'this_folder'}}

        To set advanced permissions use a list for the ``perms`` parameter, ie:

        .. code-block:: yaml

            {'user': {'perms': ['read_attributes', 'read_ea'], 'applies_to': 'this_folder'}}

        deny_perms (dict): A dictionary containing the user/group and
        permissions to deny along with the ``applies_to`` setting. Use the same
        format used for the ``grant_perms`` parameter. Remember, deny
        permissions supersede grant permissions.

        inheritance (bool): If True the object will inherit permissions from the
        parent, if False, inheritance will be disabled. Inheritance setting will
        not apply to parent directories if they must be created

    Returns:
        bool: True if successful, otherwise raise an error

    CLI Example:

    .. code-block:: bash

        # To grant the 'Users' group 'read & execute' permissions.
        salt '*' file.check_perms C:\\Temp\\ Administrators "{'Users': {'perms': 'read_execute'}}"

        # Locally using salt call
        salt-call file.check_perms C:\\Temp\\ Administrators "{'Users': {'perms': 'read_execute', 'applies_to': 'this_folder_only'}}"

        # Specify advanced attributes with a list
        salt '*' file.check_perms C:\\Temp\\ Administrators "{'jsnuffy': {'perms': ['read_attributes', 'read_ea'], 'applies_to': 'files_only'}}"
    '''
    path = os.path.expanduser(path)

    if not ret:
        ret = {'name': path,
               'changes': {},
               'comment': [],
               'result': True}
        orig_comment = ''
    else:
        orig_comment = ret['comment']
        ret['comment'] = []

    # Check owner
    if owner:
        owner = salt.utils.win_dacl.get_name(owner)
        current_owner = salt.utils.win_dacl.get_owner(path)
        if owner != current_owner:
            if __opts__['test'] is True:
                ret['pchanges']['owner'] = owner
            else:
                try:
                    salt.utils.win_dacl.set_owner(path, owner)
                    ret['changes']['owner'] = owner
                except CommandExecutionError:
                    ret['result'] = False
                    ret['comment'].append(
                        'Failed to change owner to "{0}"'.format(owner))

    # Check permissions
    cur_perms = salt.utils.win_dacl.get_permissions(path)

    # Verify Deny Permissions
    changes = {}
    if deny_perms is not None:
        for user in deny_perms:
            # Check that user exists:
            try:
                user_name = salt.utils.win_dacl.get_name(user)
            except CommandExecutionError:
                ret['comment'].append(
                    'Deny Perms: User "{0}" missing from Target System'.format(user))
                continue

            # Get the proper applies_to text
            if 'applies_to' in deny_perms[user]:
                applies_to = deny_perms[user]['applies_to']
                at_flag = salt.utils.win_dacl.flags().ace_prop['file'][applies_to]
                applies_to_text = salt.utils.win_dacl.flags().ace_prop['file'][at_flag]

            else:
                applies_to = None

            if user_name not in cur_perms:
                changes[user] = {'perms': deny_perms[user]['perms']}
                if applies_to:
                    changes[user]['applies_to'] = applies_to

            else:

                # Check Perms
                if isinstance(deny_perms[user]['perms'], six.string_types):
                    if not salt.utils.win_dacl.has_permission(
                            path, user, deny_perms[user]['perms'], 'deny'):
                        changes[user] = {'perms': deny_perms[user]['perms']}
                else:
                    for perm in deny_perms[user]['perms']:
                        if not salt.utils.win_dacl.has_permission(
                                path, user, perm, 'deny', exact=False):
                            if user not in changes:
                                changes[user] = {'perms': []}
                            changes[user]['perms'].append(deny_perms[user]['perms'])

                # Check if applies_to was passed
                if applies_to:
                    # Is there a deny permission set
                    if 'deny' in cur_perms[user_name]:
                        # If the applies to settings are different, use the new one
                        if not cur_perms[user_name]['deny']['applies to'] == applies_to_text:
                            if user not in changes:
                                changes[user] = {}
                            changes[user]['applies_to'] = applies_to

    if changes:
        ret['changes']['deny_perms'] = {}
        for user in changes:
            user_name = salt.utils.win_dacl.get_name(user)

            if __opts__['test'] is True:
                ret['pchanges']['deny_perms'][user] = changes[user]
            else:
                # Get applies_to
                applies_to = None
                if 'applies_to' not in changes[user]:
                    # Get current "applies to" settings from the file
                    if user_name in cur_perms and 'deny' in cur_perms[user_name]:
                        for flag in salt.utils.win_dacl.flags().ace_prop['file']:
                            if salt.utils.win_dacl.flags().ace_prop['file'][flag] == \
                                    cur_perms[user_name]['deny']['applies to']:
                                at_flag = flag
                                for flag1 in salt.utils.win_dacl.flags().ace_prop['file']:
                                    if salt.utils.win_dacl.flags().ace_prop['file'][flag1] == at_flag:
                                        applies_to = flag1
                    if not applies_to:
                        applies_to = 'this_folder_subfolders_files'
                else:
                    applies_to = changes[user]['applies_to']

                perms = []
                if 'perms' not in changes[user]:
                    # Get current perms
                    # Check for basic perms
                    for perm in cur_perms[user_name]['deny']['permissions']:
                        for flag in salt.utils.win_dacl.flags().ace_perms['file']['basic']:
                            if salt.utils.win_dacl.flags().ace_perms['file']['basic'][flag] == perm:
                                perm_flag = flag
                                for flag1 in salt.utils.win_dacl.flags().ace_perms['file']['basic']:
                                    if salt.utils.win_dacl.flags().ace_perms['file']['basic'][flag1] == perm_flag:
                                        perms = flag1
                    # Make a list of advanced perms
                    if not perms:
                        for perm in cur_perms[user_name]['deny']['permissions']:
                            for flag in salt.utils.win_dacl.flags().ace_perms['file']['advanced']:
                                if salt.utils.win_dacl.flags().ace_perms['file']['advanced'][flag] == perm:
                                    perm_flag = flag
                                    for flag1 in salt.utils.win_dacl.flags().ace_perms['file']['advanced']:
                                        if salt.utils.win_dacl.flags().ace_perms['file']['advanced'][flag1] == perm_flag:
                                            perms.append(flag1)
                else:
                    perms = changes[user]['perms']

                try:
                    log.debug('*' * 68)
                    log.debug(perms)
                    log.debug('*' * 68)
                    salt.utils.win_dacl.set_permissions(
                        path, user, perms, 'deny', applies_to)
                    ret['changes']['deny_perms'][user] = changes[user]
                except CommandExecutionError:
                    ret['result'] = False
                    ret['comment'].append(
                        'Failed to deny permissions for "{0}" to '
                        '{1}'.format(user, changes[user]))

    # Verify Grant Permissions
    changes = {}
    if grant_perms is not None:
        for user in grant_perms:
            # Check that user exists:
            try:
                user_name = salt.utils.win_dacl.get_name(user)
            except CommandExecutionError:
                ret['comment'].append(
                    'Grant Perms: User "{0}" missing from Target System'.format(user))
                continue

            # Get the proper applies_to text
            if 'applies_to' in grant_perms[user]:
                applies_to = grant_perms[user]['applies_to']
                at_flag = salt.utils.win_dacl.flags().ace_prop['file'][applies_to]
                applies_to_text = salt.utils.win_dacl.flags().ace_prop['file'][at_flag]

            else:
                applies_to = None

            if user_name not in cur_perms:

                changes[user] = {'perms': grant_perms[user]['perms']}
                if applies_to:
                    changes[user]['applies_to'] = applies_to

            else:

                # Check Perms
                if isinstance(grant_perms[user]['perms'], six.string_types):
                    if not salt.utils.win_dacl.has_permission(
                            path, user, grant_perms[user]['perms']):
                        changes[user] = {'perms': grant_perms[user]['perms']}
                else:
                    for perm in grant_perms[user]['perms']:
                        if not salt.utils.win_dacl.has_permission(
                                path, user, perm, exact=False):
                            if user not in changes:
                                changes[user] = {'perms': []}
                            changes[user]['perms'].append(grant_perms[user]['perms'])

                # Check if applies_to was passed
                if applies_to:
                    # Is there a deny permission set
                    if 'grant' in cur_perms[user_name]:
                        # If the applies to settings are different, use the new one
                        if not cur_perms[user_name]['grant']['applies to'] == applies_to_text:
                            if user not in changes:
                                changes[user] = {}
                            changes[user]['applies_to'] = applies_to

    if changes:
        ret['changes']['grant_perms'] = {}
        for user in changes:
            user_name = salt.utils.win_dacl.get_name(user)
            if __opts__['test'] is True:
                ret['changes']['grant_perms'][user] = changes[user]
            else:
                applies_to = None
                if 'applies_to' not in changes[user]:
                    # Get current "applies_to" settings from the file
                    if user_name in cur_perms and 'grant' in cur_perms[user_name]:
                        for flag in salt.utils.win_dacl.flags().ace_prop['file']:
                            if salt.utils.win_dacl.flags().ace_prop['file'][flag] == \
                                    cur_perms[user_name]['grant']['applies to']:
                                at_flag = flag
                                for flag1 in salt.utils.win_dacl.flags().ace_prop['file']:
                                    if salt.utils.win_dacl.flags().ace_prop['file'][flag1] == at_flag:
                                        applies_to = flag1
                    if not applies_to:
                        applies_to = 'this_folder_subfolders_files'
                else:
                    applies_to = changes[user]['applies_to']

                perms = []
                if 'perms' not in changes[user]:
                    # Check for basic perms
                    for perm in cur_perms[user_name]['grant']['permissions']:
                        for flag in salt.utils.win_dacl.flags().ace_perms['file']['basic']:
                            if salt.utils.win_dacl.flags().ace_perms['file']['basic'][flag] == perm:
                                perm_flag = flag
                                for flag1 in salt.utils.win_dacl.flags().ace_perms['file']['basic']:
                                    if salt.utils.win_dacl.flags().ace_perms['file']['basic'][flag1] == perm_flag:
                                        perms = flag1
                    # Make a list of advanced perms
                    if not perms:
                        for perm in cur_perms[user_name]['grant']['permissions']:
                            for flag in salt.utils.win_dacl.flags().ace_perms['file']['advanced']:
                                if salt.utils.win_dacl.flags().ace_perms['file']['advanced'][flag] == perm:
                                    perm_flag = flag
                                    for flag1 in salt.utils.win_dacl.flags().ace_perms['file']['advanced']:
                                        if salt.utils.win_dacl.flags().ace_perms['file']['advanced'][flag1] == perm_flag:
                                            perms.append(flag1)
                else:
                    perms = changes[user]['perms']

                try:
                    salt.utils.win_dacl.set_permissions(
                        path, user, perms, 'grant', applies_to)
                    ret['changes']['grant_perms'][user] = changes[user]
                except CommandExecutionError:
                    ret['result'] = False
                    ret['comment'].append(
                        'Failed to grant permissions for "{0}" to '
                        '{1}'.format(user, changes[user]))

    # Check inheritance
    if inheritance is not None:
        if not inheritance == salt.utils.win_dacl.get_inheritance(path):
            if __opts__['test'] is True:
                ret['changes']['inheritance'] = inheritance
            else:
                try:
                    salt.utils.win_dacl.set_inheritance(path, inheritance)
                    ret['changes']['inheritance'] = inheritance
                except CommandExecutionError:
                    ret['result'] = False
                    ret['comment'].append(
                        'Failed to set inheritance for "{0}" to '
                        '{1}'.format(path, inheritance))

    # Re-add the Original Comment if defined
    if isinstance(orig_comment, six.string_types):
        if orig_comment:
            ret['comment'].insert(0, orig_comment)
    else:
        if orig_comment:
            ret['comment'] = orig_comment.extend(ret['comment'])

    ret['comment'] = '\n'.join(ret['comment'])

    # Set result for test = True
    if __opts__['test'] is True and ret['changes']:
        ret['result'] = None

    return ret