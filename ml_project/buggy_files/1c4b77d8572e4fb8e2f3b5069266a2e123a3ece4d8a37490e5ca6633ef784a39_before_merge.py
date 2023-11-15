def list_users(verbose=True, hashes=False):
    '''
    List user accounts

    verbose : boolean
        return all information
    hashes : boolean
        include NT HASH and LM HASH in verbose output

    CLI Example:

    .. code-block:: bash

        salt '*' pdbedit.list
    '''
    users = {} if verbose else []

    if verbose:
        # parse detailed user data
        res = __salt__['cmd.run_all'](
            'pdbedit --list --verbose {hashes}'.format(hashes="--smbpasswd-style" if hashes else ""),
        )

        if res['retcode'] > 0:
            log.error(res['stderr'] if 'stderr' in res else res['stdout'])
        else:
            user_data = {}
            for user in res['stdout'].splitlines():
                if user.startswith('-'):
                    if user_data:
                        users[user_data['unix username']] = user_data
                    user_data = {}
                elif ':' in user:
                    label = user[:user.index(':')].strip().lower()
                    data = user[(user.index(':')+1):].strip()
                    user_data[label] = data

            if user_data:
                users[user_data['unix username']] = user_data
    else:
        # list users
        res = __salt__['cmd.run_all']('pdbedit --list')

        if res['retcode'] > 0:
            return {'Error': res['stderr'] if 'stderr' in res else res['stdout']}
        else:
            for user in res['stdout'].splitlines():
                users.append(user.split(':')[0])

    return users