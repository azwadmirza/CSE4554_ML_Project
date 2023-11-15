    def create(self, provider, names, **kwargs):
        '''
        Create the named VMs, without using a profile

        Example:

        .. code-block:: python

            client.create(names=['myinstance'], provider='my-ec2-config',
                kwargs={'image': 'ami-1624987f', 'size': 't1.micro',
                        'ssh_username': 'ec2-user', 'securitygroup': 'default',
                        'delvol_on_destroy': True})
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
            vm_['profile'] = None
            ret[name] = salt.utils.simple_types_filter(
                mapper.create(vm_))
        return ret