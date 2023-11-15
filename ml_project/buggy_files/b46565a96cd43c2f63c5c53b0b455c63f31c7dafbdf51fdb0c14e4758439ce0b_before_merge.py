    def start(self, core_args=None, core_env=None):
        """
        First test whether we already have a Tribler process listening on port 8085. If so, use that one and don't
        start a new, fresh session.
        """

        def on_request_error(_):
            self.use_existing_core = False
            self.start_tribler_core(core_args=core_args, core_env=core_env)

        self.events_manager.connect()
        connect(self.events_manager.reply.error, on_request_error)
        # This is a hack to determine if we have notify the user to wait for the directory fork to finish
        _, _, src_dir, tgt_dir = should_fork_state_directory(get_root_state_directory(), version_id)
        if src_dir is not None:
            # There is going to be a directory fork, so we extend the core connection timeout and notify the user
            self.events_manager.remaining_connection_attempts = 1200
            self.events_manager.change_loading_text.emit("Copying data from previous Tribler version, please wait")