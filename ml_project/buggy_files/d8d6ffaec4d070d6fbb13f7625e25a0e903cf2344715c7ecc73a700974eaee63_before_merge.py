    def run_map(self, dmap):
        '''
        Execute the contents of the VM map
        '''
        if self._has_loop(dmap):
            msg = 'Uh-oh, that cloud map has a dependency loop!'
            log.error(msg)
            raise SaltCloudException(msg)
        # Go through the create list and calc dependencies
        for key, val in six.iteritems(dmap['create']):
            log.info(
                six.u('Calculating dependencies for {0}').format(key)
            )
            level = 0
            level = self._calcdep(dmap, key, val, level)
            log.debug(
                six.u('Got execution order {0} for {1}').format(level, key)
            )
            dmap['create'][key]['level'] = level

        try:
            existing_list = six.iteritems(dmap['existing'])
        except KeyError:
            existing_list = six.iteritems({})

        for key, val in existing_list:
            log.info(
                six.u('Calculating dependencies for {0}').format(key)
            )
            level = 0
            level = self._calcdep(dmap, key, val, level)
            log.debug(
                six.u('Got execution order {0} for {1}').format(level, key)
            )
            dmap['existing'][key]['level'] = level

        # Now sort the create list based on dependencies
        create_list = sorted(six.iteritems(dmap['create']), key=lambda x: x[1]['level'])
        output = {}
        if self.opts['parallel']:
            parallel_data = []
        master_name = None
        master_minion_name = None
        master_host = None
        master_finger = None
        try:
            master_name, master_profile = next((
                (name, profile) for name, profile in create_list
                if profile.get('make_master', False) is True
            ))
            master_minion_name = master_name
            log.debug(
                six.u('Creating new master {0!r}').format(master_name)
            )
            if salt.config.get_cloud_config_value(
                'deploy',
                master_profile,
                self.opts
            ) is False:
                raise SaltCloudSystemExit(
                    'Cannot proceed with \'make_master\' when salt deployment '
                    'is disabled(ex: --no-deploy).'
                )

            # Generate the master keys
            log.debug(
                six.u('Generating master keys for {0[name]!r}').format(master_profile)
            )
            priv, pub = salt.utils.cloud.gen_keys(
                salt.config.get_cloud_config_value(
                    'keysize',
                    master_profile,
                    self.opts
                )
            )
            master_profile['master_pub'] = pub
            master_profile['master_pem'] = priv

            # Generate the fingerprint of the master pubkey in order to
            # mitigate man-in-the-middle attacks
            master_temp_pub = salt.utils.mkstemp()
            with salt.utils.fopen(master_temp_pub, 'w') as mtp:
                mtp.write(pub)
            master_finger = salt.utils.pem_finger(master_temp_pub, sum_type=self.opts['hash_type'])
            os.unlink(master_temp_pub)

            if master_profile.get('make_minion', True) is True:
                master_profile.setdefault('minion', {})
                if 'id' in master_profile['minion']:
                    master_minion_name = master_profile['minion']['id']
                # Set this minion's master as local if the user has not set it
                if 'master' not in master_profile['minion']:
                    master_profile['minion']['master'] = '127.0.0.1'
                    if master_finger is not None:
                        master_profile['master_finger'] = master_finger

            # Generate the minion keys to pre-seed the master:
            for name, profile in create_list:
                make_minion = salt.config.get_cloud_config_value(
                    'make_minion', profile, self.opts, default=True
                )
                if make_minion is False:
                    continue

                log.debug(
                    six.u('Generating minion keys for {0[name]!r}').format(profile)
                )
                priv, pub = salt.utils.cloud.gen_keys(
                    salt.config.get_cloud_config_value(
                        'keysize',
                        profile,
                        self.opts
                    )
                )
                profile['pub_key'] = pub
                profile['priv_key'] = priv
                # Store the minion's public key in order to be pre-seeded in
                # the master
                master_profile.setdefault('preseed_minion_keys', {})
                master_profile['preseed_minion_keys'].update({name: pub})

            local_master = False
            if master_profile['minion'].get('local_master', False) and \
                    master_profile['minion'].get('master', None) is not None:
                # The minion is explicitly defining a master and it's
                # explicitly saying it's the local one
                local_master = True

            out = self.create(master_profile, local_master=local_master)

            if not isinstance(out, dict):
                log.debug(
                    six.u('Master creation details is not a dictionary: {0}').format(
                        out
                    )
                )

            elif 'Errors' in out:
                raise SaltCloudSystemExit(
                    'An error occurred while creating the master, not '
                    'continuing: {0}'.format(out['Errors'])
                )

            deploy_kwargs = (
                self.opts.get('show_deploy_args', False) is True and
                # Get the needed data
                out.get('deploy_kwargs', {}) or
                # Strip the deploy_kwargs from the returned data since we don't
                # want it shown in the console.
                out.pop('deploy_kwargs', {})
            )

            master_host = deploy_kwargs.get('salt_host', deploy_kwargs.get('host', None))
            if master_host is None:
                raise SaltCloudSystemExit(
                    'Host for new master {0} was not found, '
                    'aborting map'.format(
                        master_name
                    )
                )
            output[master_name] = out
        except StopIteration:
            log.debug('No make_master found in map')
            # Local master?
            # Generate the fingerprint of the master pubkey in order to
            # mitigate man-in-the-middle attacks
            master_pub = os.path.join(self.opts['pki_dir'], 'master.pub')
            if os.path.isfile(master_pub):
                master_finger = salt.utils.pem_finger(master_pub, sum_type=self.opts['hash_type'])

        opts = self.opts.copy()
        if self.opts['parallel']:
            # Force display_ssh_output to be False since the console will
            # need to be reset afterwards
            log.info(
                'Since parallel deployment is in use, ssh console output '
                'is disabled. All ssh output will be logged though'
            )
            opts['display_ssh_output'] = False

        local_master = master_name is None

        for name, profile in create_list:
            if name in (master_name, master_minion_name):
                # Already deployed, it's the master's minion
                continue

            if 'minion' in profile and profile['minion'].get('local_master', False) and \
                    profile['minion'].get('master', None) is not None:
                # The minion is explicitly defining a master and it's
                # explicitly saying it's the local one
                local_master = True

            if master_finger is not None and local_master is False:
                profile['master_finger'] = master_finger

            if master_host is not None:
                profile.setdefault('minion', {})
                profile['minion'].setdefault('master', master_host)

            if self.opts['parallel']:
                parallel_data.append({
                    'opts': opts,
                    'name': name,
                    'profile': profile,
                    'local_master': local_master
                })
                continue

            # Not deploying in parallel
            try:
                output[name] = self.create(
                    profile, local_master=local_master
                )
                if self.opts.get('show_deploy_args', False) is False \
                        and 'deploy_kwargs' in output \
                        and isinstance(output[name], dict):
                    output[name].pop('deploy_kwargs', None)
            except SaltCloudException as exc:
                log.error(
                    six.u('Failed to deploy {0!r}. Error: {1}').format(
                        name, exc
                    ),
                    # Show the traceback if the debug logging level is enabled
                    exc_info_on_loglevel=logging.DEBUG
                )
                output[name] = {'Error': str(exc)}

        for name in dmap.get('destroy', ()):
            output[name] = self.destroy(name)

        if self.opts['parallel'] and len(parallel_data) > 0:
            if 'pool_size' in self.opts:
                pool_size = self.opts['pool_size']
            else:
                pool_size = len(parallel_data)
            log.info(
                six.u('Cloud pool size: {0}').format(pool_size)
            )
            output_multip = enter_mainloop(
                _create_multiprocessing, parallel_data, pool_size=pool_size)
            # We have deployed in parallel, now do start action in
            # correct order based on dependencies.
            if self.opts['start_action']:
                actionlist = []
                grp = -1
                for key, val in six.itervalues(groupby(iter(dmap['create'])),
                                        lambda x: x['level']):
                    actionlist.append([])
                    grp += 1
                    for item in val:
                        actionlist[grp].append(item['name'])

                out = {}
                for group in actionlist:
                    log.info(
                        six.u('Running {0} on {1}').format(
                            self.opts['start_action'], ', '.join(group)
                        )
                    )
                    client = salt.client.get_local_client()
                    out.update(client.cmd(
                        ','.join(group), self.opts['start_action'],
                        timeout=self.opts['timeout'] * 60, expr_form='list'
                    ))
                for obj in output_multip:
                    next(six.itervalues(obj))['ret'] = out[next(six.iterkeys(obj))]
                    output.update(obj)
            else:
                for obj in output_multip:
                    output.update(obj)

        return output