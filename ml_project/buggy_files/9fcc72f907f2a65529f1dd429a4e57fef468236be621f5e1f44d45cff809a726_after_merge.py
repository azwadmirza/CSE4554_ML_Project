    def connect(self):
        """Starts talking to the RTM server through a WebSocket connection"""
        if self.bot_id is None:
            self.bot_id = self.web_client.auth_test()["bot_id"]

        old_session: Optional[Connection] = self.current_session
        old_current_session_state: ConnectionState = self.current_session_state

        if self.wss_uri is None:
            self.wss_uri = self.issue_new_wss_url()

        current_session = Connection(
            url=self.wss_uri,
            logger=self.logger,
            ping_interval=self.ping_interval,
            trace_enabled=self.trace_enabled,
            all_message_trace_enabled=self.all_message_trace_enabled,
            ping_pong_trace_enabled=self.ping_pong_trace_enabled,
            receive_buffer_size=1024,
            proxy=self.proxy,
            on_message_listener=self.run_all_message_listeners,
            on_error_listener=self.run_all_error_listeners,
            on_close_listener=self.run_all_close_listeners,
            connection_type_name="RTM",
        )
        current_session.connect()

        if old_current_session_state is not None:
            old_current_session_state.terminated = True
        if old_session is not None:
            old_session.close()

        self.current_session = current_session
        self.current_session_state = ConnectionState()
        self.auto_reconnect_enabled = self.default_auto_reconnect_enabled

        if not self.current_app_monitor_started:
            self.current_app_monitor_started = True
            self.current_app_monitor.start()

        self.logger.info(
            f"A new session has been established (session id: {self.session_id()})"
        )