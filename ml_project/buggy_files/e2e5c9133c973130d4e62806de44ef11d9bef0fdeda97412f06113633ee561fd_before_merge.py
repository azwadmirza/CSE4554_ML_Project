    def _run_current_session(self):
        try:
            if self.current_session is not None and self.current_session.is_active():
                self.logger.info(
                    "Starting to receive messages from a new connection"
                    f" (session id: {self.session_id()})"
                )
                self.current_session_state.terminated = False
                self.current_session.run_until_completion(self.current_session_state)
                self.logger.info(
                    "Stopped receiving messages from a connection"
                    f" (session id: {self.session_id()})"
                )
        except Exception as e:
            self.logger.exception(
                "Failed to start or stop the current session"
                f" (session id: {self.session_id()}, error: {e})"
            )