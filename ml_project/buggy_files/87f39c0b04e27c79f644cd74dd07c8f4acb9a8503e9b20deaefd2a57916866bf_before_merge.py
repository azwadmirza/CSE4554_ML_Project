    def run(self,
            emitter: StdoutEmitter = None,
            hendrix: bool = True,
            learning: bool = True,
            availability: bool = True,
            worker: bool = True,
            pruning: bool = True,
            interactive: bool = False,
            prometheus: bool = False,
            start_reactor: bool = True
            ) -> None:

        """Schedule and start select ursula services, then optionally start the reactor."""

        #
        # Async loops ordered by schedule priority
        #

        if pruning:
            self.__pruning_task = self._arrangement_pruning_task.start(interval=self._pruning_interval, now=True)

        if learning:
            if emitter:
                emitter.message(f"Connecting to {','.join(self.learning_domains)}", color='green', bold=True)
            self.start_learning_loop(now=self._start_learning_now)

        if self._availability_check and availability:
            self._availability_sensor.start(now=False)  # wait...

        if worker and not self.federated_only:
            self.work_tracker.start(act_now=True, requirement_func=self._availability_sensor.status)

        #
        # Non-order dependant services
        #

        if prometheus:
            # TODO: Integrate with Hendrix TLS Deploy?
            # Local scoped to help prevent import without prometheus installed
            from nucypher.utilities.metrics import initialize_prometheus_exporter
            initialize_prometheus_exporter(ursula=self, port=self._metrics_port)

        if interactive and emitter:
            stdio.StandardIO(UrsulaCommandProtocol(ursula=self, emitter=emitter))

        if hendrix:

            if emitter:
                emitter.message(f"Starting Ursula on {self.rest_interface}", color='green', bold=True)

            deployer = self.get_deployer()
            deployer.addServices()
            deployer.catalogServers(deployer.hendrix)

            if not start_reactor:
                return

            if emitter:
                emitter.message("Working ~ Keep Ursula Online!", color='blue', bold=True)

            try:
                deployer.run()  # <--- Blocking Call (Reactor)
            except Exception as e:
                self.log.critical(str(e))
                if emitter:
                    emitter.message(f"{e.__class__.__name__} {e}", color='red', bold=True)
                raise  # Crash :-(

        elif start_reactor:  # ... without hendrix
            reactor.run()    # <--- Blocking Call (Reactor)