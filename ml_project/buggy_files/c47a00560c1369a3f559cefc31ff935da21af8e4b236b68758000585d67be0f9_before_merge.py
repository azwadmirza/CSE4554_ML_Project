def load_config(module, command_filter, commit=False, replace=False,
                comment=None, admin=False, running=None, nc_get_filter=None,
                label=None):

    conn = get_connection(module)

    diff = None
    if is_netconf(module):
        # FIXME: check for platform behaviour and restore this
        # conn.lock(target = 'candidate')
        # conn.discard_changes()

        try:
            for filter in to_list(command_filter):
                conn.edit_config(filter)

            candidate = get_config(module, source='candidate', config_filter=nc_get_filter)
            diff = get_config_diff(module, running, candidate)

            if commit and diff:
                commit_config(module)
            else:
                discard_config(module)
        except ConnectionError as exc:
            module.fail_json(msg=to_text(exc, errors='surrogate_then_replace'))
        finally:
            # conn.unlock(target = 'candidate')
            pass

    elif is_cliconf(module):
        # to keep the pre-cliconf behaviour, make a copy, avoid adding commands to input list
        cmd_filter = deepcopy(command_filter)
        # If label is present check if label already exist before entering
        # config mode
        try:
            if label:
                old_label = check_existing_commit_labels(conn, label)
                if old_label:
                    module.fail_json(
                        msg='commit label {%s} is already used for'
                        ' an earlier commit, please choose a different label'
                        ' and rerun task' % label
                    )
            cmd_filter.insert(0, 'configure terminal')
            if admin:
                cmd_filter.insert(0, 'admin')

            conn.edit_config(cmd_filter)
            if module._diff:
                diff = get_config_diff(module)

            if replace:
                cmd = list()
                cmd.append({'command': 'commit replace',
                            'prompt': 'This commit will replace or remove the entire running configuration',
                            'answer': 'yes'})
                cmd.append('end')
                conn.edit_config(cmd)
            elif commit:
                commit_config(module, comment=comment, label=label)
                conn.edit_config('end')
                if admin:
                    conn.edit_config('exit')
            else:
                conn.discard_changes()
        except ConnectionError as exc:
            module.fail_json(msg=to_text(exc, errors='surrogate_then_replace'))

    return diff