def delete(name, remove=False, force=False, root=None):
    '''
    Remove a user from the minion

    CLI Example:

    .. code-block:: bash

        salt '*' user.delete name remove=True force=True
    '''
    cmd = ['userdel']

    if remove:
        cmd.append('-r')

    if force and __grains__['kernel'] != 'OpenBSD':
        cmd.append('-f')

    cmd.append(name)

    if root is not None:
        cmd.extend(('-R', root))

    ret = __salt__['cmd.run_all'](cmd, python_shell=False)

    if ret['retcode'] == 0:
        # Command executed with no errors
        return True

    if ret['retcode'] == 12:
        # There's a known bug in Debian based distributions, at least, that
        # makes the command exit with 12, see:
        #  https://bugs.launchpad.net/ubuntu/+source/shadow/+bug/1023509
        if __grains__['os_family'] not in ('Debian',):
            return False

        if 'var/mail' in ret['stderr'] or 'var/spool/mail' in ret['stderr']:
            # We've hit the bug, let's log it and not fail
            log.debug(
                'While the userdel exited with code 12, this is a known bug on '
                'debian based distributions. See http://goo.gl/HH3FzT'
            )
            return True

    return False