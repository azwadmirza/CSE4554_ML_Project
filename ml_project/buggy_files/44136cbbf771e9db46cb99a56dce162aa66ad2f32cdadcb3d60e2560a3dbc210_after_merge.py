    def check_authentication(self, load, auth_type, key=None, show_username=False):
        '''
        .. versionadded:: Oxygen

        Go through various checks to see if the token/eauth/user can be authenticated.

        Returns a dictionary containing the following keys:

        - auth_list
        - username
        - error

        If an error is encountered, return immediately with the relevant error dictionary
        as authentication has failed. Otherwise, return the username and valid auth_list.
        '''
        auth_list = []
        username = load.get('username', 'UNKNOWN')
        ret = {'auth_list': auth_list,
               'username': username,
               'error': {}}

        # Authenticate
        if auth_type == 'token':
            token = self.authenticate_token(load)
            if not token:
                ret['error'] = {'name': 'TokenAuthenticationError',
                                'message': 'Authentication failure of type "token" occurred.'}
                return ret

            # Update username for token
            username = token['name']
            ret['username'] = username
            auth_list = self.get_auth_list(load, token=token)
        elif auth_type == 'eauth':
            if not self.authenticate_eauth(load):
                ret['error'] = {'name': 'EauthAuthenticationError',
                                'message': 'Authentication failure of type "eauth" occurred for '
                                           'user {0}.'.format(username)}
                return ret

            auth_list = self.get_auth_list(load)
        elif auth_type == 'user':
            auth_ret = self.authenticate_key(load, key)
            msg = 'Authentication failure of type "user" occurred'
            if not auth_ret:  # auth_ret can be a boolean or the effective user id
                if show_username:
                    msg = '{0} for user {1}.'.format(msg, username)
                ret['error'] = {'name': 'UserAuthenticationError', 'message': msg}
                return ret

            # Verify that the caller has root on master
            if auth_ret is not True:
                if AuthUser(load['user']).is_sudo():
                    if not self.opts['sudo_acl'] or not self.opts['publisher_acl']:
                        auth_ret = True

            if auth_ret is not True:
                # Avoid a circular import
                import salt.utils.master
                auth_list = salt.utils.master.get_values_of_matching_keys(
                    self.opts['publisher_acl'], auth_ret)
                if not auth_list:
                    ret['error'] = {'name': 'UserAuthenticationError', 'message': msg}
                    return ret
        else:
            ret['error'] = {'name': 'SaltInvocationError',
                            'message': 'Authentication type not supported.'}
            return ret

        # Authentication checks passed
        ret['auth_list'] = auth_list
        return ret