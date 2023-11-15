    def run_code(self, code, global_dict):
        options = self.options
        verbose = self.verbose
        ofile = self.ofile

        tracer = VizTracer(
            tracer_entries=options.tracer_entries,
            verbose=verbose,
            output_file=ofile,
            max_stack_depth=options.max_stack_depth,
            exclude_files=options.exclude_files,
            include_files=options.include_files,
            ignore_c_function=options.ignore_c_function,
            ignore_non_file=options.ignore_non_file,
            log_return_value=options.log_return_value,
            log_function_args=options.log_function_args,
            log_print=options.log_print,
            log_gc=options.log_gc,
            novdb=options.novdb,
            pid_suffix=options.pid_suffix
        )

        self.tracer = tracer

        builtins.__dict__["__viz_tracer__"] = tracer

        self.parent_pid = os.getpid()
        if options.log_multiprocess:
            if get_start_method() != "fork":
                return False, "Only fork based multiprocess is supported"
            self.patch_multiprocessing(tracer)

        def term_handler(signalnum, frame):
            self.exit_routine()
        signal.signal(signal.SIGTERM, term_handler)

        atexit.register(self.exit_routine)
        if options.log_sparse:
            tracer.enable = True
        else:
            tracer.start()
        exec(code, global_dict)
        tracer.stop()

        self.exit_routine()