    def __init__(
        self,
        shutdown_server_event,
        loadable_target_origin=None,
        heartbeat=False,
        heartbeat_timeout=30,
    ):
        super(DagsterApiServer, self).__init__()

        check.bool_param(heartbeat, 'heartbeat')
        check.int_param(heartbeat_timeout, 'heartbeat_timeout')
        check.invariant(heartbeat_timeout > 0, 'heartbeat_timeout must be greater than 0')

        self._shutdown_server_event = check.inst_param(
            shutdown_server_event, 'shutdown_server_event', seven.ThreadingEventType
        )
        self._loadable_target_origin = check.opt_inst_param(
            loadable_target_origin, 'loadable_target_origin', LoadableTargetOrigin
        )

        if loadable_target_origin:
            loadable_targets = get_loadable_targets(
                loadable_target_origin.python_file,
                loadable_target_origin.module_name,
                loadable_target_origin.working_directory,
                loadable_target_origin.attribute,
            )
            self._loadable_repository_symbols = [
                LoadableRepositorySymbol(
                    attribute=loadable_target.attribute,
                    repository_name=repository_def_from_target_def(
                        loadable_target.target_definition
                    ).name,
                )
                for loadable_target in loadable_targets
            ]
        else:
            self._loadable_repository_symbols = []

        self._shutdown_server_event = check.inst_param(
            shutdown_server_event, 'shutdown_server_event', seven.ThreadingEventType
        )
        # Dict[str, multiprocessing.Process] of run_id to execute_run process
        self._executions = {}
        # Dict[str, multiprocessing.Event]
        self._termination_events = {}
        self._execution_lock = threading.Lock()

        self._repository_code_pointer_dict = {}
        for loadable_repository_symbol in self._loadable_repository_symbols:
            if self._loadable_target_origin.python_file:
                self._repository_code_pointer_dict[
                    loadable_repository_symbol.repository_name
                ] = CodePointer.from_python_file(
                    self._loadable_target_origin.python_file,
                    loadable_repository_symbol.attribute,
                    self._loadable_target_origin.working_directory,
                )
            if self._loadable_target_origin.module_name:
                self._repository_code_pointer_dict[
                    loadable_repository_symbol.repository_name
                ] = CodePointer.from_module(
                    self._loadable_target_origin.module_name, loadable_repository_symbol.attribute,
                )

        self.__last_heartbeat_time = time.time()
        if heartbeat:
            self.__heartbeat_thread = threading.Thread(
                target=heartbeat_thread,
                args=(heartbeat_timeout, self.__last_heartbeat_time, self._shutdown_server_event),
            )
            self.__heartbeat_thread.daemon = True
            self.__heartbeat_thread.start()
        else:
            self.__heartbeat_thread = None