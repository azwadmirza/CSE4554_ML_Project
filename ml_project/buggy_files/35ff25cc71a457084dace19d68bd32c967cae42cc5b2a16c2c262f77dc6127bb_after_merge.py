    def action(
        self,
        fun=None,
        cloudmap=None,
        names=None,
        provider=None,
        instance=None,
        kwargs=None
    ):
        '''
        Execute a single action via the cloud plugin backend

        Examples:

        .. code-block:: python

            client.action(fun='show_instance', names=['myinstance'])
            client.action(fun='show_image', provider='my-ec2-config',
                kwargs={'image': 'ami-10314d79'}
            )
        '''
        mapper = salt.cloud.Map(self._opts_defaults(action=fun, names=names))
        if instance:
            if names:
                raise SaltCloudConfigError(
                    'Please specify either a list of \'names\' or a single '
                    '\'instance\', but not both.'
                )
            names = [instance]

        if names and not provider:
            self.opts['action'] = fun
            return mapper.do_action(names, kwargs)

        if provider and not names:
            return mapper.do_function(provider, fun, kwargs)
        else:
            # This should not be called without either an instance or a
            # provider. If both an instance/list of names and a provider
            # are given, then we also need to exit. We can only have one
            # or the other.
            raise SaltCloudConfigError(
                'Either an instance (or list of names) or a provider must be '
                'specified, but not both.'
            )