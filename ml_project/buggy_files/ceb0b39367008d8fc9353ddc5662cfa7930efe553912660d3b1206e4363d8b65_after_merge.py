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

        self._shutdown_server_event = check.inst_param(
            shutdown_server_event, 'shutdown_server_event', seven.ThreadingEventType
        )
        # Dict[str, multiprocessing.Process] of run_id to execute_run process
        self._executions = {}
        # Dict[str, multiprocessing.Event]
        self._termination_events = {}
        self._execution_lock = threading.Lock()

        self._repository_symbols_and_code_pointers = LazyRepositorySymbolsAndCodePointers(
            loadable_target_origin
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