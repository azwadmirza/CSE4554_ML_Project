    def connect(self) -> None:
        old_session: Optional[Connection] = self.current_session

        if self.wss_uri is None:
            self.wss_uri = self.issue_new_wss_url()

        self.current_session = Connection(
            url=self.wss_uri,
            logger=self.logger,
            ping_interval=self.ping_interval,
            trace_enabled=self.trace_enabled,
            all_message_trace_enabled=self.all_message_trace_enabled,
            ping_pong_trace_enabled=self.ping_pong_trace_enabled,
            receive_buffer_size=self.receive_buffer_size,
            proxy=self.proxy,
            proxy_headers=self.proxy_headers,
            on_message_listener=self._on_message,
            on_error_listener=self._on_error,
            on_close_listener=self._on_close,
        )
        self.current_session.connect()
        self.auto_reconnect_enabled = self.default_auto_reconnect_enabled

        if old_session is not None:
            old_session.close()
            self.current_session_state.terminated = True

        if not self.current_app_monitor_started:
            self.current_app_monitor_started = True
            self.current_app_monitor.start()

        self.logger.info(
            f"A new session has been established (session id: {self.session_id()})"
        )