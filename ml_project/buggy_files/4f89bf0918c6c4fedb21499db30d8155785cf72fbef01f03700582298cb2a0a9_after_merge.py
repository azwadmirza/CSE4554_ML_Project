def load_config(module, commands, commit=False, replace=False, comment=None):

    rc, out, err = exec_command(module, 'configure terminal')
    if rc != 0:
        module.fail_json(msg='unable to enter configuration mode', err=err)

    failed = False
    for command in to_list(commands):
        if command == 'end':
            continue

        rc, out, err = exec_command(module, command)
        if rc != 0:
            failed = True
            break

    if failed:
        exec_command(module, 'abort')
        module.fail_json(msg=err, commands=commands, rc=rc)

    rc, diff, err = exec_command(module, 'show commit changes diff')
    if commit:
        cmd = 'commit'
        if comment:
            cmd += ' comment {0}'.format(comment)
    else:
        cmd = 'abort'
        diff = None
    exec_command(module, cmd)

    return diff