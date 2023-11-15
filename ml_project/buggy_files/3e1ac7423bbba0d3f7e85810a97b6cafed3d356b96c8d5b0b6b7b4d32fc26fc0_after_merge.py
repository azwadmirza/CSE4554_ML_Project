    def run_profile(self, profile, names, vm_overrides=None):
        '''
        Parse over the options passed on the command line and determine how to
        handle them
        '''
        if profile not in self.opts['profiles']:
            msg = 'Profile {0} is not defined'.format(profile)
            log.error(msg)
            return {'Error': msg}

        ret = {}
        if not vm_overrides:
            vm_overrides = {}

        try:
            with salt.utils.fopen(self.opts['conf_file'], 'r') as mcc:
                main_cloud_config = yaml.safe_load(mcc)
            if not main_cloud_config:
                main_cloud_config = {}
        except KeyError:
            main_cloud_config = {}
        except IOError:
            main_cloud_config = {}

        if main_cloud_config is None:
            main_cloud_config = {}

        mapped_providers = self.map_providers_parallel()
        profile_details = self.opts['profiles'][profile]
        vms = {}
        for prov, val in six.iteritems(mapped_providers):
            prov_name = next(iter(val))
            for node in mapped_providers[prov][prov_name]:
                vms[node] = mapped_providers[prov][prov_name][node]
                vms[node]['provider'] = prov
                vms[node]['driver'] = prov_name
        alias, driver = profile_details['provider'].split(':')

        provider_details = self.opts['providers'][alias][driver].copy()
        del provider_details['profiles']

        for name in names:
            if name in vms:
                prov = vms[name]['provider']
                driv = vms[name]['driver']
                msg = six.u('{0} already exists under {1}:{2}').format(
                    name, prov, driv
                )
                log.error(msg)
                ret[name] = {'Error': msg}
                continue

            vm_ = main_cloud_config.copy()
            vm_.update(provider_details)
            vm_.update(profile_details)
            vm_.update(vm_overrides)

            vm_['name'] = name
            if self.opts['parallel']:
                process = multiprocessing.Process(
                    target=self.create,
                    args=(vm_,)
                )
                process.start()
                ret[name] = {
                    'Provisioning': 'VM being provisioned in parallel. '
                                    'PID: {0}'.format(process.pid)
                }
                continue

            try:
                # No need to inject __active_provider_name__ into the context
                # here because self.create takes care of that
                ret[name] = self.create(vm_)
                if not ret[name]:
                    ret[name] = {'Error': 'Failed to deploy VM'}
                    if len(names) == 1:
                        raise SaltCloudSystemExit('Failed to deploy VM')
                    continue
                if self.opts.get('show_deploy_args', False) is False:
                    ret[name].pop('deploy_kwargs', None)
            except (SaltCloudSystemExit, SaltCloudConfigError) as exc:
                if len(names) == 1:
                    raise
                ret[name] = {'Error': str(exc)}

        return ret