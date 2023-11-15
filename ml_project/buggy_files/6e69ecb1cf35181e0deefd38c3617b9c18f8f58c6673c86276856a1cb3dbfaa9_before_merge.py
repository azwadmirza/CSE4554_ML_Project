    def __init__(self, window: WindowLike, configs: ConfigRegistry, documents: DocumentHandler,
                 diagnostics: WindowDiagnostics, session_starter: 'Callable', sublime: 'Any',
                 handler_dispatcher, on_closed: 'Optional[Callable]' = None) -> None:

        # to move here:
        # configurations.py: window_client_configs and all references
        self._window = window
        self._configs = configs
        self._diagnostics = diagnostics
        self._documents = documents
        self._sessions = dict()  # type: Dict[str, Session]
        self._start_session = session_starter
        self._sublime = sublime
        self._handlers = handler_dispatcher
        self._restarting = False
        self._project_path = get_project_path(self._window)
        self._diagnostics.set_on_updated(
            lambda file_path, client_name:
                global_events.publish("document.diagnostics",
                                      DiagnosticsUpdate(self._window, client_name, file_path)))
        self._on_closed = on_closed
        self._is_closing = False
        self._initialization_lock = threading.Lock()