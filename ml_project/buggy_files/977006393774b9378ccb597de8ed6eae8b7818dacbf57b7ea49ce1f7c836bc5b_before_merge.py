    def __init__(self,
                 tracer_entries=1000000,
                 verbose=1,
                 max_stack_depth=-1,
                 include_files=None,
                 exclude_files=None,
                 ignore_c_function=False,
                 ignore_non_file=False,
                 log_return_value=False,
                 log_function_args=False,
                 log_print=False,
                 log_gc=False,
                 novdb=False,
                 pid_suffix=False,
                 file_info=False,
                 output_file="result.html"):
        super().__init__(
                tracer_entries=tracer_entries,
                max_stack_depth=max_stack_depth,
                include_files=include_files,
                exclude_files=exclude_files,
                ignore_c_function=ignore_c_function,
                ignore_non_file=ignore_non_file,
                log_return_value=log_return_value,
                log_print=log_print,
                log_gc=log_gc,
                novdb=novdb,
                log_function_args=log_function_args
        )
        self.verbose = verbose
        self.pid_suffix = pid_suffix
        self.file_info = file_info
        self.output_file = output_file
        self.system_print = None