    def _process_loop(self):
        '''
        The process loop is called off of the main thread and will not exit
        unless the main agent is shutdown.
        '''

        _log.debug("Starting process loop.")
        self._setup_backup_db()
        self.historian_setup()

        # now that everything is setup we need to make sure that the topics
        # are syncronized between


        #Based on the state of the back log and whether or not sucessful
        #publishing is currently happening (and how long it's taking)
        #we may or may not want to wait on the event queue for more input
        #before proceeding with the rest of the loop.
        #wait_for_input = not bool(self._get_outstanding_to_publish())
        wait_for_input = not bool(self._get_outstanding_to_publish())

        while True:
            try:
                _log.debug("Reading from/waiting for queue.")
                new_to_publish = [self._event_queue.get(wait_for_input, self._retry_period)]
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

            self._backup_new_to_publish(new_to_publish)

            wait_for_input = True
            start_time = datetime.utcnow()
            
            _log.debug("Calling publish_to_historian.")
            while True:
                to_publish_list = self._get_outstanding_to_publish()
                if not to_publish_list:
                    break
                
                try:
                    self.publish_to_historian(to_publish_list)
                except Exception:
                    _log.exception("An unhandled exception occured while " \
                               "publishing to the historian.")
                
                if not self._any_sucessfull_publishes():
                    break
                self._cleanup_successful_publishes()

                now = datetime.utcnow()
                if now - start_time > self._max_time_publishing:
                    wait_for_input = False
                    break
        _log.debug("Finished processing")