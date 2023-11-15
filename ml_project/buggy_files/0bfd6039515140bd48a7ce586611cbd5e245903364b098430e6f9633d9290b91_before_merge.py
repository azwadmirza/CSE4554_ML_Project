    def unhandled_error_observer(self, event):
        """
        This method is called when an unhandled error in Tribler is observed. Broadcasts the tribler_exception event.
        """
        if event['isError']:
            text = ""
            if 'log_legacy' in event and 'log_text' in event:
                text = event['log_text']
            elif 'log_failure' in event:
                text = str(event['log_failure'])

            # There are some errors that we are ignoring.
            # No route to host: this issue is non-critical since Tribler can still function when a request fails.
            if 'socket.error: [Errno 113]' in text:
                self._logger.error("Observed no route to host error (but ignoring)."
                                   "This might indicate a problem with your firewall.")
                return

            # Socket block: this sometimes occurres on Windows and is non-critical.
            if 'socket.error: [Errno %s]' % SOCKET_BLOCK_ERRORCODE in text:
                self._logger.error("Unable to send data due to socket.error %s", SOCKET_BLOCK_ERRORCODE)
                return

            if 'socket.error: [Errno 51]' in text:
                self._logger.error("Could not send data: network is unreachable.")
                return

            if self.lm.api_manager and len(text) > 0:
                self.lm.api_manager.root_endpoint.events_endpoint.on_tribler_exception(text)
                self.lm.api_manager.root_endpoint.state_endpoint.on_tribler_exception(text)