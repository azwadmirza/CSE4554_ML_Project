    def handle_event(self, package):
        '''
        Handle an event from the epull_sock (all local minion events)
        '''
        log.debug('Handling event {0!r}'.format(package))
        if package.startswith('module_refresh'):
            tag, data = salt.utils.event.MinionEvent.unpack(package)
            self.module_refresh(notify=data.get('notify', False))
        elif package.startswith('pillar_refresh'):
            yield self.pillar_refresh()
        elif package.startswith('manage_schedule'):
            self.manage_schedule(package)
        elif package.startswith('manage_beacons'):
            self.manage_beacons(package)
        elif package.startswith('grains_refresh'):
            if self.grains_cache != self.opts['grains']:
                self.pillar_refresh(force_refresh=True)
                self.grains_cache = self.opts['grains']
        elif package.startswith('environ_setenv'):
            self.environ_setenv(package)
        elif package.startswith('_minion_mine'):
            self._mine_send(package)
        elif package.startswith('fire_master'):
            tag, data = salt.utils.event.MinionEvent.unpack(package)
            log.debug('Forwarding master event tag={tag}'.format(tag=data['tag']))
            self._fire_master(data['data'], data['tag'], data['events'], data['pretag'])
        elif package.startswith('__master_disconnected'):
            tag, data = salt.utils.event.MinionEvent.unpack(package)
            # if the master disconnect event is for a different master, raise an exception
            if data['master'] != self.opts['master']:
                raise Exception()
            if self.connected:
                # we are not connected anymore
                self.connected = False
                # modify the scheduled job to fire only on reconnect
                schedule = {
                   'function': 'status.master',
                   'seconds': self.opts['master_alive_interval'],
                   'jid_include': True,
                   'maxrunning': 2,
                   'kwargs': {'master': self.opts['master'],
                              'connected': False}
                }
                self.schedule.modify_job(name='__master_alive',
                                         schedule=schedule)

                log.info('Connection to master {0} lost'.format(self.opts['master']))

                if self.opts['master_type'] == 'failover':
                    log.info('Trying to tune in to next master from master-list')

                    if hasattr(self, 'pub_channel'):
                        self.pub_channel.on_recv(None)
                        if hasattr(self.pub_channel, 'close'):
                            self.pub_channel.close()
                        del self.pub_channel

                    # if eval_master finds a new master for us, self.connected
                    # will be True again on successful master authentication
                    master, self.pub_channel = yield self.eval_master(
                                                        opts=self.opts,
                                                        failed=True)
                    if self.connected:
                        self.opts['master'] = master

                        # re-init the subsystems to work with the new master
                        log.info('Re-initialising subsystems for new '
                                 'master {0}'.format(self.opts['master']))
                        self.functions, self.returners, self.function_errors = self._load_modules()
                        self.pub_channel.on_recv(self._handle_payload)
                        self._fire_master_minion_start()
                        log.info('Minion is ready to receive requests!')

                        # update scheduled job to run with the new master addr
                        schedule = {
                           'function': 'status.master',
                           'seconds': self.opts['master_alive_interval'],
                           'jid_include': True,
                           'maxrunning': 2,
                           'kwargs': {'master': self.opts['master'],
                                      'connected': True}
                        }
                        self.schedule.modify_job(name='__master_alive',
                                                 schedule=schedule)

        elif package.startswith('__master_connected'):
            # handle this event only once. otherwise it will pollute the log
            if not self.connected:
                log.info('Connection to master {0} re-established'.format(self.opts['master']))
                self.connected = True
                # modify the __master_alive job to only fire,
                # if the connection is lost again
                schedule = {
                   'function': 'status.master',
                   'seconds': self.opts['master_alive_interval'],
                   'jid_include': True,
                   'maxrunning': 2,
                   'kwargs': {'master': self.opts['master'],
                              'connected': True}
                }

                self.schedule.modify_job(name='__master_alive',
                                         schedule=schedule)
        elif package.startswith('_salt_error'):
            tag, data = salt.utils.event.MinionEvent.unpack(package)
            log.debug('Forwarding salt error event tag={tag}'.format(tag=tag))
            self._fire_master(data, tag)