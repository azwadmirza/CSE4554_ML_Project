    def _opts_defaults(self, **kwargs):
        '''
        Set the opts dict to defaults and allow for opts to be overridden in
        the kwargs
        '''
        # Let's start with the default salt cloud configuration
        opts = salt.config.CLOUD_CONFIG_DEFAULTS.copy()
        # Update it with the loaded configuration
        opts.update(self.opts.copy())
        # Reset some of the settings to sane values
        opts['parallel'] = False
        opts['keep_tmp'] = False
        opts['deploy'] = True
        opts['update_bootstrap'] = False
        opts['show_deploy_args'] = False
        opts['script_args'] = ''
        # Update it with the passed kwargs
        if 'kwargs' in kwargs:
            opts.update(kwargs['kwargs'])
        opts.update(kwargs)
        profile = opts.get('profile', None)
        # filter other profiles if one is specified
        if profile:
            for _profile in [a for a in opts.get('profiles', {})]:
                if not _profile == profile:
                    opts['profiles'].pop(_profile)
            # if profile is specified and we have enough info about providers
            # also filter them to speedup methods like
            # __filter_non_working_providers
            providers = [a.get('provider', '').split(':')[0]
                         for a in six.itervalues(opts['profiles'])
                         if a.get('provider', '')]
            if providers:
                _providers = opts.get('providers', {})
                for provider in _providers.keys():
                    if provider not in providers:
                        _providers.pop(provider)
        return opts