    def eval_master(self,
                    opts,
                    timeout=60,
                    safe=True,
                    failed=False):
        '''
        Evaluates and returns a tuple of the current master address and the pub_channel.

        In standard mode, just creates a pub_channel with the given master address.

        With master_type=func evaluates the current master address from the given
        module and then creates a pub_channel.

        With master_type=failover takes the list of masters and loops through them.
        The first one that allows the minion to create a pub_channel is then
        returned. If this function is called outside the minions initialization
        phase (for example from the minions main event-loop when a master connection
        loss was detected), 'failed' should be set to True. The current
        (possibly failed) master will then be removed from the list of masters.
        '''
        # check if master_type was altered from its default
        if opts['master_type'] != 'str' and opts['__role'] != 'syndic':
            # check for a valid keyword
            if opts['master_type'] == 'func':
                # split module and function and try loading the module
                mod, fun = opts['master'].split('.')
                try:
                    master_mod = salt.loader.raw_mod(opts, mod, fun)
                    if not master_mod:
                        raise TypeError
                    # we take whatever the module returns as master address
                    opts['master'] = master_mod[mod + '.' + fun]()
                except TypeError:
                    msg = ('Failed to evaluate master address from '
                           'module \'{0}\''.format(opts['master']))
                    log.error(msg)
                    sys.exit(salt.defaults.exitcodes.EX_GENERIC)
                log.info('Evaluated master from module: {0}'.format(master_mod))

            # if failover is set, master has to be of type list
            elif opts['master_type'] == 'failover':
                if isinstance(opts['master'], list):
                    log.info('Got list of available master addresses:'
                             ' {0}'.format(opts['master']))
                    if opts['master_shuffle']:
                        shuffle(opts['master'])
                # if opts['master'] is a str and we have never created opts['master_list']
                elif isinstance(opts['master'], str) and ('master_list' not in opts):
                    # We have a string, but a list was what was intended. Convert.
                    # See issue 23611 for details
                    opts['master'] = [opts['master']]
                elif opts['__role'] == 'syndic':
                    log.info('Syndic setting master_syndic to \'{0}\''.format(opts['master']))

                # if failed=True, the minion was previously connected
                # we're probably called from the minions main-event-loop
                # because a master connection loss was detected. remove
                # the possibly failed master from the list of masters.
                elif failed:
                    log.info('Removing possibly failed master {0} from list of'
                             ' masters'.format(opts['master']))
                    # create new list of master with the possibly failed one removed
                    opts['master'] = [x for x in opts['master_list'] if opts['master'] != x]

                else:
                    msg = ('master_type set to \'failover\' but \'master\' '
                           'is not of type list but of type '
                           '{0}'.format(type(opts['master'])))
                    log.error(msg)
                    sys.exit(salt.defaults.exitcodes.EX_GENERIC)
                # If failover is set, minion have to failover on DNS errors instead of retry DNS resolve.
                # See issue 21082 for details
                if opts['retry_dns']:
                    msg = ('\'master_type\' set to \'failover\' but \'retry_dns\' is not 0. '
                           'Setting \'retry_dns\' to 0 to failover to the next master on DNS errors.')
                    log.critical(msg)
                    opts['retry_dns'] = 0
            else:
                msg = ('Invalid keyword \'{0}\' for variable '
                       '\'master_type\''.format(opts['master_type']))
                log.error(msg)
                sys.exit(salt.defaults.exitcodes.EX_GENERIC)

        # Specify kwargs for the channel factory so that SMinion doesn't need to define an io_loop
        # (The channel factories will set a default if the kwarg isn't passed)
        factory_kwargs = {'timeout': timeout, 'safe': safe}
        if getattr(self, 'io_loop', None):
            factory_kwargs['io_loop'] = self.io_loop

        # if we have a list of masters, loop through them and be
        # happy with the first one that allows us to connect
        if isinstance(opts['master'], list):
            conn = False
            # shuffle the masters and then loop through them
            local_masters = copy.copy(opts['master'])

            for master in local_masters:
                opts['master'] = master
                opts.update(prep_ip_port(opts))
                opts.update(resolve_dns(opts))
                self.opts = opts

                # on first run, update self.opts with the whole master list
                # to enable a minion to re-use old masters if they get fixed
                if 'master_list' not in opts:
                    opts['master_list'] = local_masters

                try:
                    pub_channel = salt.transport.client.AsyncPubChannel.factory(opts, **factory_kwargs)
                    yield pub_channel.connect()
                    conn = True
                    break
                except SaltClientError:
                    msg = ('Master {0} could not be reached, trying '
                           'next master (if any)'.format(opts['master']))
                    log.info(msg)
                    continue

            if not conn:
                self.connected = False
                msg = ('No master could be reached or all masters denied '
                       'the minions connection attempt.')
                log.error(msg)
            else:
                self.tok = pub_channel.auth.gen_token('salt')
                self.connected = True
                raise tornado.gen.Return((opts['master'], pub_channel))

        # single master sign in
        else:
            opts.update(prep_ip_port(opts))
            opts.update(resolve_dns(opts))
            pub_channel = salt.transport.client.AsyncPubChannel.factory(self.opts, **factory_kwargs)
            yield pub_channel.connect()
            self.tok = pub_channel.auth.gen_token('salt')
            self.connected = True
            raise tornado.gen.Return((opts['master'], pub_channel))