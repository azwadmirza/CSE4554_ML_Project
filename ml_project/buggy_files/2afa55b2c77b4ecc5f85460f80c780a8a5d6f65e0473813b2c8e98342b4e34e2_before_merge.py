    def _configure_node_from_config(self, config):
        """
        Startup elements in the node as specified in the provided node configuration.
        """
        self.log.info('Configuring node from local configuration ...')

        # get contoller configuration subpart
        controller = config.get('controller', {})

        # start Manhole in node controller
        if 'manhole' in controller:
            yield self._controller.call(u'crossbar.start_manhole', controller['manhole'], options=CallOptions())
            self.log.debug("controller: manhole started")

        # startup all workers
        workers = config.get('workers', [])
        if len(workers):
            self.log.info('Starting {nworkers} workers ...', nworkers=len(workers))
        else:
            self.log.info('No workers configured!')
        for worker in workers:

            # worker ID
            if 'id' in worker:
                worker_id = worker.pop('id')
            else:
                worker_id = 'worker-{:03d}'.format(self._worker_no)
                self._worker_no += 1

            # worker type - a type of working process from the following fixed list
            worker_type = worker['type']
            assert worker_type in self._native_workers
            worker_cfg = self._native_workers[worker_type]

            # set logname depending on worker type
            worker_logname = "{} '{}'".format(worker_cfg['logname'], worker_id)

            # any worker specific options
            worker_options = worker.get('options', {})

            # now actually start the worker ..
            yield self._controller.call(u'crossbar.start_worker', worker_id, worker_type, worker_options, options=CallOptions())

            # native worker processes setup
            if worker_type in self._native_workers:

                # setup native worker generic stuff
                method_name = '_configure_native_worker_{}'.format(worker_type.replace('-', '_'))
                try:
                    config_fn = getattr(self, method_name)
                except AttributeError:
                    raise ValueError(
                        "A native worker of type '{}' is configured but "
                        "there is no method '{}' on {}".format(worker_type, method_name, type(self))
                    )
                yield config_fn(worker_logname, worker_id, worker)

        self.log.info('Local node configuration applied successfully!')