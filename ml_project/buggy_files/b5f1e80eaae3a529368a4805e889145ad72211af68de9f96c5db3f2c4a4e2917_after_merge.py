  def make_remote_decorator(num_return_vals, num_cpus, num_gpus, func_id=None):
    def remote_decorator(func):
      func_name = "{}.{}".format(func.__module__, func.__name__)
      if func_id is None:
        function_id = compute_function_id(func_name, func)
      else:
        function_id = func_id

      def func_call(*args, **kwargs):
        """This gets run immediately when a worker calls a remote function."""
        check_connected()
        check_main_thread()
        args = list(args)
        # Fill in the remaining arguments.
        args.extend([kwargs[keyword] if keyword in kwargs else default
                     for keyword, default in keyword_defaults[len(args):]])
        if any([arg is funcsigs._empty for arg in args]):
          raise Exception("Not enough arguments were provided to {}."
                          .format(func_name))
        if _mode() == PYTHON_MODE:
          # In PYTHON_MODE, remote calls simply execute the function. We copy
          # the arguments to prevent the function call from mutating them and
          # to match the usual behavior of immutable remote objects.
          try:
            _env()._running_remote_function_locally = True
            result = func(*copy.deepcopy(args))
          finally:
            _env()._reinitialize()
            _env()._running_remote_function_locally = False
          return result
        objectids = _submit_task(function_id, func_name, args)
        if len(objectids) == 1:
          return objectids[0]
        elif len(objectids) > 1:
          return objectids

      def func_executor(arguments):
        """This gets run when the remote function is executed."""
        result = func(*arguments)
        return result

      def func_invoker(*args, **kwargs):
        """This is used to invoke the function."""
        raise Exception("Remote functions cannot be called directly. Instead "
                        "of running '{}()', try '{}.remote()'."
                        .format(func_name, func_name))
      func_invoker.remote = func_call
      func_invoker.executor = func_executor
      func_invoker.is_remote = True
      func_name = "{}.{}".format(func.__module__, func.__name__)
      func_invoker.func_name = func_name
      if sys.version_info >= (3, 0):
        func_invoker.__doc__ = func.__doc__
      else:
        func_invoker.func_doc = func.func_doc

      sig_params = [(k, v) for k, v
                    in funcsigs.signature(func).parameters.items()]
      keyword_defaults = [(k, v.default) for k, v in sig_params]
      has_vararg_param = any([v.kind == v.VAR_POSITIONAL
                              for k, v in sig_params])
      func_invoker.has_vararg_param = has_vararg_param
      has_kwargs_param = any([v.kind == v.VAR_KEYWORD for k, v in sig_params])
      check_signature_supported(has_kwargs_param, has_vararg_param,
                                keyword_defaults, func_name)

      # Everything ready - export the function
      if worker.mode in [SCRIPT_MODE, SILENT_MODE]:
        export_remote_function(function_id, func_name, func, num_return_vals,
                               num_cpus, num_gpus)
      elif worker.mode is None:
        worker.cached_remote_functions.append((function_id, func_name, func,
                                               num_return_vals, num_cpus,
                                               num_gpus))
      return func_invoker

    return remote_decorator