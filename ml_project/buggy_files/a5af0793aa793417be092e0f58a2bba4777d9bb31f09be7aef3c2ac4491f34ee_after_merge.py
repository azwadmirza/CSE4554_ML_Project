    def get_auth_list(self, load, token=None):
        '''
        Retrieve access list for the user specified in load.
        The list is built by eauth module or from master eauth configuration.
        Return None if current configuration doesn't provide any ACL for the user. Return an empty
        list if the user has no rights to execute anything on this master and returns non-empty list
        if user is allowed to execute particular functions.
        '''
        # Get auth list from token
        if token and self.opts['keep_acl_in_token'] and 'auth_list' in token:
            return token['auth_list']
        # Get acl from eauth module.
        auth_list = self.__get_acl(load)
        if auth_list is not None:
            return auth_list

        eauth = token['eauth'] if token else load['eauth']
        if eauth not in self.opts['external_auth']:
            # No matching module is allowed in config
            log.warning('Authorization failure occurred.')
            return None

        if token:
            name = token['name']
            groups = token.get('groups')
        else:
            name = self.load_name(load)  # The username we are attempting to auth with
            groups = self.get_groups(load)  # The groups this user belongs to
        eauth_config = self.opts['external_auth'][eauth]
        if not groups:
            groups = []

        # We now have an authenticated session and it is time to determine
        # what the user has access to.
        auth_list = self.ckminions.fill_auth_list(
                eauth_config,
                name,
                groups)

        auth_list = self.__process_acl(load, auth_list)

        log.trace("Compiled auth_list: {0}".format(auth_list))

        return auth_list