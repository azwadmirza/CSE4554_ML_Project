    def func_wrapper(*args, **kwargs):
        '''
        Wrap gpg function calls to fix permissions
        '''
        user = kwargs.get('user')
        gnupghome = kwargs.get('gnupghome')

        if not gnupghome:
            gnupghome = _get_user_gnupghome(user)

        userinfo = _get_user_info(user)
        run_user = _get_user_info()

        if userinfo['uid'] != run_user['uid'] and os.path.exists(gnupghome):
            # Given user is different from one who runs Salt process,
            # need to fix ownership permissions for GnuPG home dir
            group = __salt__['file.gid_to_group'](run_user['gid'])
            for path in [gnupghome] + __salt__['file.find'](gnupghome):
                __salt__['file.chown'](path, run_user['name'], group)

        # Filter special kwargs
        for key in list(kwargs):
            if key.startswith('__'):
                del kwargs[key]

        ret = func(*args, **kwargs)

        if userinfo['uid'] != run_user['uid']:
            group = __salt__['file.gid_to_group'](userinfo['gid'])
            for path in [gnupghome] + __salt__['file.find'](gnupghome):
                __salt__['file.chown'](path, user, group)

        return ret