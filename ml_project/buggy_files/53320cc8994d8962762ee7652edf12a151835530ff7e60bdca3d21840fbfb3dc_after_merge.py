    def check_state(self) -> None:
        try:
            if self.sock is not None:
                try:
                    self.ping(f"{self.session_id}:{time.time()}")
                except ssl.SSLZeroReturnError as e:
                    self.logger.info(
                        "Unable to send a ping message. Closing the connection..."
                        f" (session id: {self.session_id}, reason: {e})"
                    )
                    self.disconnect()
                    return

                if self.last_ping_pong_time is not None:
                    disconnected_seconds = int(time.time() - self.last_ping_pong_time)
                    if self.trace_enabled and disconnected_seconds > self.ping_interval:
                        message = (
                            f"{disconnected_seconds} seconds have passed "
                            f"since this client last received a pong response from the server "
                            f"(session id: {self.session_id})"
                        )
                        self.logger.debug(message)

                    is_stale = disconnected_seconds > self.ping_interval * 4
                    if is_stale:
                        self.logger.info(
                            "The connection seems to be stale. Disconnecting..."
                            f" (session id: {self.session_id},"
                            f" reason: disconnected for {disconnected_seconds}+ seconds)"
                        )
                        self.disconnect()
                        return
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