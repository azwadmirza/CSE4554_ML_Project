    def _start_client(self, config: ClientConfig):
        project_path = get_project_path(self._window)
        if project_path is None:
            debug('Cannot start without a project folder')
            return

        if not self._can_start_config(config.name):
            debug('Already starting on this window:', config.name)
            return

        if not self._handlers.on_start(config.name, self._window):
            return

        self._window.status_message("Starting " + config.name + "...")
        debug("starting in", project_path)
        session = None  # type: Optional[Session]
        try:
            session = self._start_session(
                window=self._window,
                project_path=project_path,
                config=config,
                on_pre_initialize=self._handle_pre_initialize,
                on_post_initialize=self._handle_post_initialize,
                on_post_exit=self._handle_post_exit)
        except Exception as e:
            message = "\n\n".join([
                "Could not start {}",
                "{}",
                "Server will be disabled for this window"
            ]).format(config.name, str(e))

            self._configs.disable(config.name)
            self._sublime.message_dialog(message)

        if session:
            debug("window {} added session {}".format(self._window.id(), config.name))
            self._sessions[config.name] = session