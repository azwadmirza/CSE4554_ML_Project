    def create(self, vm_, local_master=True):
        '''
        Create a single VM
        '''
        output = {}

        minion_dict = salt.config.get_cloud_config_value(
            'minion', vm_, self.opts, default={}
        )

        alias, driver = vm_['provider'].split(':')
        fun = '{0}.create'.format(driver)
        if fun not in self.clouds:
            log.error(
                'Creating \'{0[name]}\' using \'{0[provider]}\' as the provider '
                'cannot complete since \'{1}\' is not available'.format(
                    vm_,
                    driver
                )
            )
            return

        deploy = salt.config.get_cloud_config_value('deploy', vm_, self.opts)
        make_master = salt.config.get_cloud_config_value(
            'make_master',
            vm_,
            self.opts
        )

        if deploy:
            if not make_master and 'master' not in minion_dict:
                log.warning(
                    'There\'s no master defined on the \'{0}\' VM settings.'.format(
                        vm_['name']
                    )
                )

            if 'pub_key' not in vm_ and 'priv_key' not in vm_:
                log.debug('Generating minion keys for \'{0[name]}\''.format(vm_))
                priv, pub = salt.utils.cloud.gen_keys(
                    salt.config.get_cloud_config_value(
                        'keysize',
                        vm_,
                        self.opts
                    )
                )
                vm_['pub_key'] = pub
                vm_['priv_key'] = priv
        else:
            # Note(pabelanger): We still reference pub_key and priv_key when
            # deploy is disabled.
            vm_['pub_key'] = None
            vm_['priv_key'] = None

        key_id = minion_dict.get('id', vm_['name'])

        domain = vm_.get('domain')
        if vm_.get('use_fqdn') and domain:
            minion_dict['append_domain'] = domain

        if 'append_domain' in minion_dict:
            key_id = '.'.join([key_id, minion_dict['append_domain']])

        if make_master is True and 'master_pub' not in vm_ and 'master_pem' not in vm_:
            log.debug(
                'Generating the master keys for \'{0[name]}\''.format(
                    vm_
                )
            )
            master_priv, master_pub = salt.utils.cloud.gen_keys(
                salt.config.get_cloud_config_value(
                    'keysize',
                    vm_,
                    self.opts
                )
            )
            vm_['master_pub'] = master_pub
            vm_['master_pem'] = master_priv

        if local_master is True and deploy is True:
            # Accept the key on the local master
            salt.utils.cloud.accept_key(
                self.opts['pki_dir'], vm_['pub_key'], key_id
            )

        vm_['os'] = salt.config.get_cloud_config_value(
            'script',
            vm_,
            self.opts
        )

        try:
            vm_['inline_script'] = salt.config.get_cloud_config_value(
                'inline_script',
                vm_,
                self.opts
            )
        except KeyError:
            pass

        try:
            alias, driver = vm_['provider'].split(':')
            func = '{0}.create'.format(driver)
            with context.func_globals_inject(
                self.clouds[fun],
                __active_provider_name__=':'.join([alias, driver])
            ):
                output = self.clouds[func](vm_)
            if output is not False and 'sync_after_install' in self.opts:
                if self.opts['sync_after_install'] not in (
                        'all', 'modules', 'states', 'grains'):
                    log.error('Bad option for sync_after_install')
                    return output

                # A small pause helps the sync work more reliably
                time.sleep(3)

                start = int(time.time())
                while int(time.time()) < start + 60:
                    # We'll try every <timeout> seconds, up to a minute
                    mopts_ = salt.config.DEFAULT_MINION_OPTS
                    conf_path = '/'.join(self.opts['conf_file'].split('/')[:-1])
                    mopts_.update(
                        salt.config.minion_config(
                            os.path.join(conf_path,
                                         'minion')
                        )
                    )

                    client = salt.client.get_local_client(mopts=self.opts)

                    ret = client.cmd(
                        vm_['name'],
                        'saltutil.sync_{0}'.format(self.opts['sync_after_install']),
                        timeout=self.opts['timeout']
                    )
                    if ret:
                        log.info(
                            six.u('Synchronized the following dynamic modules: '
                                  '  {0}').format(ret)
                        )
                        break
        except KeyError as exc:
            log.exception(
                'Failed to create VM {0}. Configuration value {1} needs '
                'to be set'.format(
                    vm_['name'], exc
                )
            )
        # If it's a map then we need to respect the 'requires'
        # so we do it later
        try:
            opt_map = self.opts['map']
        except KeyError:
            opt_map = False
        if self.opts['parallel'] and self.opts['start_action'] and not opt_map:
            log.info(
                'Running {0} on {1}'.format(
                    self.opts['start_action'], vm_['name']
                )
            )
            client = salt.client.get_local_client(mopts=self.opts)
            action_out = client.cmd(
                vm_['name'],
                self.opts['start_action'],
                timeout=self.opts['timeout'] * 60
            )
            output['ret'] = action_out
        return output