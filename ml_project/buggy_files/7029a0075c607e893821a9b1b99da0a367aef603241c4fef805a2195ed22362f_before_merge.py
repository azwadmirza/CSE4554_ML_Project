    def tune_in(self, start=True):
        '''
        Lock onto the publisher. This is the main event loop for the minion
        :rtype : None
        '''
        self._pre_tune()

        # Properly exit if a SIGTERM is signalled
        signal.signal(signal.SIGTERM, self.clean_die)

        # start up the event publisher, so we can see events during startup
        self.event_publisher = salt.utils.event.AsyncEventPublisher(
            self.opts,
            self.handle_event,
            io_loop=self.io_loop,
        )

        log.debug('Minion {0!r} trying to tune in'.format(self.opts['id']))

        if start:
            self.sync_connect_master()
        if hasattr(self, 'connected') and self.connected:
            self._fire_master_minion_start()
            log.info('Minion is ready to receive requests!')

        # Make sure to gracefully handle SIGUSR1
        enable_sigusr1_handler()

        # Make sure to gracefully handle CTRL_LOGOFF_EVENT
        salt.utils.enable_ctrl_logoff_handler()

        # On first startup execute a state run if configured to do so
        self._state_run()

        loop_interval = self.opts['loop_interval']

        try:
            if self.opts['grains_refresh_every']:  # If exists and is not zero. In minutes, not seconds!
                if self.opts['grains_refresh_every'] > 1:
                    log.debug(
                        'Enabling the grains refresher. Will run every {0} minutes.'.format(
                            self.opts['grains_refresh_every'])
                    )
                else:  # Clean up minute vs. minutes in log message
                    log.debug(
                        'Enabling the grains refresher. Will run every {0} minute.'.format(
                            self.opts['grains_refresh_every'])

                    )
                self._refresh_grains_watcher(
                    abs(self.opts['grains_refresh_every'])
                )
        except Exception as exc:
            log.error(
                'Exception occurred in attempt to initialize grain refresh routine during minion tune-in: {0}'.format(
                    exc)
            )

        self.periodic_callbacks = {}
        # schedule the stuff that runs every interval
        ping_interval = self.opts.get('ping_interval', 0) * 60
        if ping_interval > 0:
            def ping_master():
                try:
                    self._fire_master('ping', 'minion_ping')
                except Exception:
                    log.warning('Attempt to ping master failed.', exc_on_loglevel=logging.DEBUG)
            self.periodic_callbacks['ping'] = tornado.ioloop.PeriodicCallback(ping_master, ping_interval * 1000, io_loop=self.io_loop)

        self.periodic_callbacks['cleanup'] = tornado.ioloop.PeriodicCallback(self._fallback_cleanups, loop_interval * 1000, io_loop=self.io_loop)

        def handle_beacons():
            # Process Beacons
            beacons = None
            try:
                beacons = self.process_beacons(self.functions)
            except Exception:
                log.critical('The beacon errored: ', exc_info=True)
            if beacons:
                self._fire_master(events=beacons)

        self.periodic_callbacks['beacons'] = tornado.ioloop.PeriodicCallback(handle_beacons, loop_interval * 1000, io_loop=self.io_loop)

        # TODO: actually listen to the return and change period
        def handle_schedule():
            self.process_schedule(self, loop_interval)
        if hasattr(self, 'schedule'):
            self.periodic_callbacks['schedule'] = tornado.ioloop.PeriodicCallback(handle_schedule, 1000, io_loop=self.io_loop)

        # start all the other callbacks
        for periodic_cb in six.itervalues(self.periodic_callbacks):
            periodic_cb.start()

        # add handler to subscriber
        if hasattr(self, 'pub_channel'):
            self.pub_channel.on_recv(self._handle_payload)
        else:
            log.error('No connection to master found. Scheduled jobs will not run.')

        if start:
            try:
                self.io_loop.start()
            except (KeyboardInterrupt, RuntimeError):  # A RuntimeError can be re-raised by Tornado on shutdown
                self.destroy()