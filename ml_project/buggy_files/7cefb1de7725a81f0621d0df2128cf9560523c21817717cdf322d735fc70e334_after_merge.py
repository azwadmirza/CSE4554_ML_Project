    def run(self):
        """Run the monitor.

        This function loops forever, checking for messages about dead database
        clients and cleaning up state accordingly.
        """
        # Initialize the subscription channel.
        self.subscribe(DB_CLIENT_TABLE_NAME)
        self.subscribe(LOCAL_SCHEDULER_INFO_CHANNEL)
        self.subscribe(PLASMA_MANAGER_HEARTBEAT_CHANNEL)
        self.subscribe(DRIVER_DEATH_CHANNEL)

        # Scan the database table for dead database clients. NOTE: This must be
        # called before reading any messages from the subscription channel.
        # This ensures that we start in a consistent state, since we may have
        # missed notifications that were sent before we connected to the
        # subscription channel.
        self.scan_db_client_table()
        # If there were any dead clients at startup, clean up the associated
        # state in the state tables.
        if len(self.dead_local_schedulers) > 0:
            self.cleanup_task_table()
        if len(self.dead_plasma_managers) > 0:
            self.cleanup_object_table()
        log.debug("{} dead local schedulers, {} plasma managers total, {} "
                  "dead plasma managers".format(
                      len(self.dead_local_schedulers),
                      (len(self.live_plasma_managers) +
                       len(self.dead_plasma_managers)),
                      len(self.dead_plasma_managers)))

        # Handle messages from the subscription channels.
        while True:
            # Process autoscaling actions
            if self.autoscaler:
                self.autoscaler.update()
            # Record how many dead local schedulers and plasma managers we had
            # at the beginning of this round.
            num_dead_local_schedulers = len(self.dead_local_schedulers)
            num_dead_plasma_managers = len(self.dead_plasma_managers)
            # Process a round of messages.
            self.process_messages()
            # If any new local schedulers or plasma managers were marked as
            # dead in this round, clean up the associated state.
            if len(self.dead_local_schedulers) > num_dead_local_schedulers:
                self.cleanup_task_table()
            if len(self.dead_plasma_managers) > num_dead_plasma_managers:
                self.cleanup_object_table()

            # Handle plasma managers that timed out during this round.
            plasma_manager_ids = list(self.live_plasma_managers.keys())
            for plasma_manager_id in plasma_manager_ids:
                if ((self.live_plasma_managers[plasma_manager_id]) >=
                        ray._config.num_heartbeats_timeout()):
                    log.warn("Timed out {}".format(PLASMA_MANAGER_CLIENT_TYPE))
                    # Remove the plasma manager from the managers whose
                    # heartbeats we're tracking.
                    del self.live_plasma_managers[plasma_manager_id]
                    # Remove the plasma manager from the db_client table. The
                    # corresponding state in the object table will be cleaned
                    # up once we receive the notification for this db_client
                    # deletion.
                    self.redis.execute_command("RAY.DISCONNECT",
                                               plasma_manager_id)

            # Increment the number of heartbeats that we've missed from each
            # plasma manager.
            for plasma_manager_id in self.live_plasma_managers:
                self.live_plasma_managers[plasma_manager_id] += 1

            # Wait for a heartbeat interval before processing the next round of
            # messages.
            time.sleep(ray._config.heartbeat_timeout_milliseconds() * 1e-3)