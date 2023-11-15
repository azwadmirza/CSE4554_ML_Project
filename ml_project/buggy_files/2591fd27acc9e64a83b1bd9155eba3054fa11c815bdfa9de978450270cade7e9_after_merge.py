    def _process_loop(self):
        """
        The process loop is called off of the main thread and will not exit
        unless the main agent is shutdown or the Agent is reconfigured.
        """

        _log.debug("Starting process loop.")

        # Sets up the concrete historian
        # call this method even in case of readonly mode in case historian
        # is setting up connections that are shared for both query and write
        # operations
        self.historian_setup()

        if self._readonly:
            _log.info("Historian setup in readonly mode.")
            return

        # Record the names of data, topics, meta tables in a metadata table
        self.record_table_definitions(self.volttron_table_defs)
        backupdb = BackupDatabase(self, self._backup_storage_limit_gb)

        # now that everything is setup we need to make sure that the topics
        # are synchronized between

        # Based on the state of the back log and whether or not successful
        # publishing is currently happening (and how long it's taking)
        # we may or may not want to wait on the event queue for more input
        # before proceeding with the rest of the loop.
        wait_for_input = not bool(
            backupdb.get_outstanding_to_publish(self._submit_size_limit))

        while True:
            try:
                _log.debug("Reading from/waiting for queue.")
                new_to_publish = [
                    self._event_queue.get(wait_for_input, self._retry_period)]
            except Empty:
                _log.debug("Queue wait timed out. Falling out.")
                new_to_publish = []

            if new_to_publish:
                _log.debug("Checking for queue build up.")
                while True:
                    try:
                        new_to_publish.append(self._event_queue.get_nowait())
                    except Empty:
                        break


            #We wake the thread after a configuration change by passing a None to the queue.
            #Backup anything new before checking for a stop.
            backupdb.backup_new_data((x for x in new_to_publish if x is not None))

            #Check for a stop for reconfiguration.
            if self._stop_process_loop:
                break

            wait_for_input = True
            start_time = datetime.utcnow()

            while True:
                to_publish_list = backupdb.get_outstanding_to_publish(
                    self._submit_size_limit)

                # Check for a stop for reconfiguration.
                if not to_publish_list or self._stop_process_loop:
                    break

                try:
                    self.publish_to_historian(to_publish_list)
                except Exception as exp:
                    _log.exception(
                        "An unhandled exception occured while publishing.")

                # if the successful queue is empty then we need not remove
                # them from the database.
                if not self._successful_published:
                    break

                backupdb.remove_successfully_published(
                    self._successful_published, self._submit_size_limit)
                self._successful_published = set()
                now = datetime.utcnow()
                if now - start_time > self._max_time_publishing:
                    wait_for_input = False
                    break

                # Check for a stop for reconfiguration.
                if self._stop_process_loop:
                    break

            # Check for a stop for reconfiguration.
            if self._stop_process_loop:
                break

        backupdb.close()
        self.historian_teardown()

        _log.debug("Process loop stopped.")