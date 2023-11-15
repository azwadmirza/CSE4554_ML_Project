def set_perms(path, grant_perms=None, deny_perms=None, inheritance=True):
    '''
    Set permissions for the given path

    Args:

        path (str): The full path to the directory.

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
        salt '*' file.set_perms C:\\Temp\\ "{'Users': {'perms': 'read_execute'}}"

        # Locally using salt call
        salt-call file.set_perms C:\\Temp\\ "{'Users': {'perms': 'read_execute', 'applies_to': 'this_folder_only'}}"

        # Specify advanced attributes with a list
        salt '*' file.set_perms C:\\Temp\\ "{'jsnuffy': {'perms': ['read_attributes', 'read_ea'], 'applies_to': 'this_folder_only'}}"
    '''
    ret = {}

    # Get the DACL for the directory
    dacl = salt.utils.win_dacl.dacl(path)

    # Get current file/folder permissions
    cur_perms = salt.utils.win_dacl.get_permissions(path)

    # Set 'deny' perms if any
    if deny_perms is not None:
        ret['deny'] = {}
        for user in deny_perms:
            # Check that user exists:
            try:
                user_name = salt.utils.win_dacl.get_name(user)
            except CommandExecutionError:
                log.debug('Deny Perms: User "{0}" missing from Target System'.format(user))
                continue

            # Get applies_to
            applies_to = None
            if 'applies_to' not in deny_perms[user]:
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
                applies_to = deny_perms[user]['applies_to']

            # Deny permissions
            if dacl.add_ace(user, 'deny', deny_perms[user]['perms'],
                            applies_to):
                ret['deny'][user] = deny_perms[user]

    # Set 'grant' perms if any
    if grant_perms is not None:
        ret['grant'] = {}
        for user in grant_perms:
            # Check that user exists:
            try:
                user_name = salt.utils.win_dacl.get_name(user)
            except CommandExecutionError:
                log.debug('Grant Perms: User "{0}" missing from Target System'.format(user))
                continue

            # Get applies_to
            applies_to = None
            if 'applies_to' not in grant_perms[user]:
                # Get current "applies to" settings from the file
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
                applies_to = grant_perms[user]['applies_to']

            # Grant permissions
            if dacl.add_ace(user, 'grant', grant_perms[user]['perms'],
                            applies_to):
                ret['grant'][user] = grant_perms[user]

    # Order the ACL
    dacl.order_acl()

    # Save the DACL, setting the inheritance
    # you have to invert inheritance because dacl.save is looking for
    # protected. protected True means Inherited False...

    if dacl.save(path, not inheritance):
        return ret

    return {}