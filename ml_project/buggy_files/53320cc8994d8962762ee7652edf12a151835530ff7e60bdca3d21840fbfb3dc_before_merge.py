    def check_state(self) -> None:
        try:
            if self.sock is not None:
                is_stale = (
                    self.last_ping_pong_time is not None
                    and time.time() - self.last_ping_pong_time > self.ping_interval * 2
                )
                if is_stale:
                    self.logger.info(
                        "The connection seems to be stale. Disconnecting..."
                        f" (session id: {self.session_id})"
                    )
                    self.disconnect()
                else:
                    self.ping(f"{self.session_id}:{time.time()}")
            else:
                self.logger.debug(
                    "This connection is already closed."
                    f" (session id: {self.session_id})"
                )
            self.consecutive_check_state_error_count = 0
        except Exception as e:
            self.logger.exception(
                "Failed to check the state of sock "
                f"(session id: {self.session_id}, error: {type(e).__name__}, message: {e})"
            )
            self.consecutive_check_state_error_count += 1
            if self.consecutive_check_state_error_count >= 5:
                self.disconnect()