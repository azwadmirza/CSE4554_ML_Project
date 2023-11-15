    def __init__(self, path=None, opts=None, config_dir=None, pillars=None):
        if opts:
            self.opts = opts
        else:
            self.opts = salt.config.cloud_config(path)

        # Check the cache-dir exists. If not, create it.
        v_dirs = [self.opts['cachedir']]
        salt.utils.verify.verify_env(v_dirs, salt.utils.get_user())

        if pillars:
            for name, provider in six.iteritems(pillars.pop('providers', {})):
                driver = provider['driver']
                provider['profiles'] = {}
                self.opts['providers'].update({name: {driver: provider}})
            for name, profile in six.iteritems(pillars.pop('profiles', {})):
                provider = profile['provider'].split(':')[0]
                driver = next(six.iterkeys(self.opts['providers'][provider]))
                profile['provider'] = '{0}:{1}'.format(provider, driver)
                profile['profile'] = name
                self.opts['profiles'].update({name: profile})
                self.opts['providers'][provider][driver]['profiles'].update({name: profile})
            self.opts.update(pillars)