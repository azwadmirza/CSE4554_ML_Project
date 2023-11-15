    def create(self, provider, names, **kwargs):
        '''
        Create the named VMs, without using a profile

        Example:

        .. code-block:: python

            client.create(provider='my-ec2-config', names=['myinstance'],
                image='ami-1624987f', size='t1.micro', ssh_username='ec2-user',
                securitygroup='default', delvol_on_destroy=True)
        '''
        mapper = salt.cloud.Map(self._opts_defaults())
        providers = self.opts['providers']
        if provider in providers:
            provider += ':{0}'.format(next(six.iterkeys(providers[provider])))
        else:
            return False
        if isinstance(names, str):
            names = names.split(',')
        ret = {}
        for name in names:
            vm_ = kwargs.copy()
            vm_['name'] = name
            vm_['driver'] = provider

            # This function doesn't require a profile, but many cloud drivers
            # check for profile information (which includes the provider key) to
            # help with config file debugging and setting up instances. Setting
            # the profile and provider defaults here avoids errors in other
            # cloud functions relying on these keys. See SaltStack Issue #41971
            # and PR #38166 for more information.
            vm_['profile'] = None
            vm_['provider'] = provider

            ret[name] = salt.utils.simple_types_filter(
                mapper.create(vm_))
        return ret