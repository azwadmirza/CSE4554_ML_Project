def _check_directory_win(name,
                         win_owner,
                         win_perms=None,
                         win_deny_perms=None,
                         win_inheritance=None):
    '''
    Check what changes need to be made on a directory
    '''
    changes = {}

    if not os.path.isdir(name):
        changes = {'directory': 'new'}
    else:
        # Check owner
        owner = salt.utils.win_dacl.get_owner(name)
        if not owner.lower() == win_owner.lower():
            changes['owner'] = win_owner

        # Check perms
        perms = salt.utils.win_dacl.get_permissions(name)

        # Verify Permissions
        if win_perms is not None:
            for user in win_perms:
                # Check that user exists:
                try:
                    salt.utils.win_dacl.get_name(user)
                except CommandExecutionError:
                    continue

                grant_perms = []
                # Check for permissions
                if isinstance(win_perms[user]['perms'], six.string_types):
                    if not salt.utils.win_dacl.has_permission(
                            name, user, win_perms[user]['perms']):
                        grant_perms = win_perms[user]['perms']
                else:
                    for perm in win_perms[user]['perms']:
                        if not salt.utils.win_dacl.has_permission(
                                name, user, perm, exact=False):
                            grant_perms.append(win_perms[user]['perms'])
                if grant_perms:
                    if 'grant_perms' not in changes:
                        changes['grant_perms'] = {}
                    if user not in changes['grant_perms']:
                        changes['grant_perms'][user] = {}
                    changes['grant_perms'][user]['perms'] = grant_perms

                # Check Applies to
                if 'applies_to' not in win_perms[user]:
                    applies_to = 'this_folder_subfolders_files'
                else:
                    applies_to = win_perms[user]['applies_to']

                if user in perms:
                    user = salt.utils.win_dacl.get_name(user)

                    # Get the proper applies_to text
                    at_flag = salt.utils.win_dacl.Flags.ace_prop['file'][applies_to]
                    applies_to_text = salt.utils.win_dacl.Flags.ace_prop['file'][at_flag]

                    if 'grant' in perms[user]:
                        if not perms[user]['grant']['applies to'] == applies_to_text:
                            if 'grant_perms' not in changes:
                                changes['grant_perms'] = {}
                            if user not in changes['grant_perms']:
                                changes['grant_perms'][user] = {}
                            changes['grant_perms'][user]['applies_to'] = applies_to

        # Verify Deny Permissions
        if win_deny_perms is not None:
            for user in win_deny_perms:
                # Check that user exists:
                try:
                    salt.utils.win_dacl.get_name(user)
                except CommandExecutionError:
                    continue

                deny_perms = []
                # Check for permissions
                if isinstance(win_deny_perms[user]['perms'], six.string_types):
                    if not salt.utils.win_dacl.has_permission(
                            name, user, win_deny_perms[user]['perms'], 'deny'):
                        deny_perms = win_deny_perms[user]['perms']
                else:
                    for perm in win_deny_perms[user]['perms']:
                        if not salt.utils.win_dacl.has_permission(
                                name, user, perm, 'deny', exact=False):
                            deny_perms.append(win_deny_perms[user]['perms'])
                if deny_perms:
                    if 'deny_perms' not in changes:
                        changes['deny_perms'] = {}
                    if user not in changes['deny_perms']:
                        changes['deny_perms'][user] = {}
                    changes['deny_perms'][user]['perms'] = deny_perms

                # Check Applies to
                if 'applies_to' not in win_deny_perms[user]:
                    applies_to = 'this_folder_subfolders_files'
                else:
                    applies_to = win_deny_perms[user]['applies_to']

                if user in perms:
                    user = salt.utils.win_dacl.get_name(user)

                    # Get the proper applies_to text
                    at_flag = salt.utils.win_dacl.Flags.ace_prop['file'][applies_to]
                    applies_to_text = salt.utils.win_dacl.Flags.ace_prop['file'][at_flag]

                    if 'deny' in perms[user]:
                        if not perms[user]['deny']['applies to'] == applies_to_text:
                            if 'deny_perms' not in changes:
                                changes['deny_perms'] = {}
                            if user not in changes['deny_perms']:
                                changes['deny_perms'][user] = {}
                            changes['deny_perms'][user]['applies_to'] = applies_to

        # Check inheritance
        if win_inheritance is not None:
            if not win_inheritance == salt.utils.win_dacl.get_inheritance(name):
                changes['inheritance'] = win_inheritance

    if changes:
        return None, 'The directory "{0}" will be changed'.format(name), changes

    return True, 'The directory {0} is in the correct state'.format(name), changes