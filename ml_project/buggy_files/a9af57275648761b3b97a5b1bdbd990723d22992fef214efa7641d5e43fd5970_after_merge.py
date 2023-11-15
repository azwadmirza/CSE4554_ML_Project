    def __init__(self, config=None, **defaults):
        # configure loggers first
        cls = self.__class__
        self.logger = logging.getLogger('%s.%s' % (cls.__module__, cls.__name__))
        self.error_logger = logging.getLogger('elasticapm.errors')
        self.state = ClientState()

        self.instrumentation_store = None
        self.processors = []
        self.filter_exception_types_dict = {}
        self._send_timer = None
        self._transports = {}
        self._service_info = None

        self.config = Config(config, default_dict=defaults)
        if self.config.errors:
            for msg in self.config.errors.values():
                self.error_logger.error(msg)
            self.config.disable_send = True

        self._transport_class = import_string(self.config.transport_class)

        for exc_to_filter in (self.config.filter_exception_types or []):
            exc_to_filter_type = exc_to_filter.split(".")[-1]
            exc_to_filter_module = ".".join(exc_to_filter.split(".")[:-1])
            self.filter_exception_types_dict[exc_to_filter_type] = exc_to_filter_module

        self.processors = [import_string(p) for p in self.config.processors] if self.config.processors else []

        if platform.python_implementation() == 'PyPy':
            # PyPy introduces a `_functools.partial.__call__` frame due to our use
            # of `partial` in AbstractInstrumentedModule
            skip_modules = ('elasticapm.', '_functools')
        else:
            skip_modules = ('elasticapm.',)

        def frames_collector_func():
            return self._get_stack_info_for_trace(
                stacks.iter_stack_frames(skip_top_modules=skip_modules),
                library_frame_context_lines=self.config.source_lines_span_library_frames,
                in_app_frame_context_lines=self.config.source_lines_span_app_frames,
                with_locals=self.config.collect_local_variables in ('all', 'transactions'),
                locals_processor_func=lambda local_var: varmap(lambda k, v: shorten(
                    v,
                    list_length=self.config.local_var_list_max_length,
                    string_length=self.config.local_var_max_length,
                ), local_var)
            )

        self.instrumentation_store = TransactionsStore(
            frames_collector_func=frames_collector_func,
            collect_frequency=self.config.flush_interval,
            sample_rate=self.config.transaction_sample_rate,
            max_spans=self.config.transaction_max_spans,
            span_frames_min_duration=self.config.span_frames_min_duration_ms,
            max_queue_size=self.config.max_queue_size,
            ignore_patterns=self.config.transactions_ignore_patterns,
        )
        self.include_paths_re = stacks.get_path_regex(self.config.include_paths) if self.config.include_paths else None
        self.exclude_paths_re = stacks.get_path_regex(self.config.exclude_paths) if self.config.exclude_paths else None
        compat.atexit_register(self.close)