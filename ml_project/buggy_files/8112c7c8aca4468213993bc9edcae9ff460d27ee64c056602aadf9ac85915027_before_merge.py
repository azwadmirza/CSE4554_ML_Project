def remote(*args, **kwargs):
  """This decorator is used to create remote functions.

  Args:
    num_return_vals (int): The number of object IDs that a call to this
      function should return.
    num_cpus (int): The number of CPUs needed to execute this function. This
      should only be passed in when defining the remote function on the driver.
    num_gpus (int): The number of GPUs needed to execute this function. This
      should only be passed in when defining the remote function on the driver.
  """
  worker = global_worker

  def make_remote_decorator(num_return_vals, num_cpus, num_gpus, func_id=None):
    def remote_decorator(func):
      func_name = "{}.{}".format(func.__module__, func.__name__)
      if func_id is None:
        # Compute the function ID as a hash of the function name as well as the
        # source code. We could in principle hash in the values in the closure
        # of the function, but that is likely to introduce non-determinism in
        # the computation of the function ID.
        function_id_hash = hashlib.sha1()
        function_id_hash.update(func_name.encode("ascii"))
        function_id_hash.update(inspect.getsource(func).encode("ascii"))
        function_id = function_id_hash.digest()
        assert len(function_id) == 20
        function_id = FunctionID(function_id)
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

  num_return_vals = (kwargs["num_return_vals"] if "num_return_vals"
                     in kwargs.keys() else 1)
  num_cpus = kwargs["num_cpus"] if "num_cpus" in kwargs.keys() else 1
  num_gpus = kwargs["num_gpus"] if "num_gpus" in kwargs.keys() else 0

  if _mode() == WORKER_MODE:
    if "function_id" in kwargs:
      function_id = kwargs["function_id"]
      return make_remote_decorator(num_return_vals, num_cpus, num_gpus,
                                   function_id)

  if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
    # This is the case where the decorator is just @ray.remote.
    return make_remote_decorator(num_return_vals, num_cpus, num_gpus)(args[0])
  else:
    # This is the case where the decorator is something like
    # @ray.remote(num_return_vals=2).
    error_string = ("The @ray.remote decorator must be applied either with no "
                    "arguments and no parentheses, for example '@ray.remote', "
                    "or it must be applied using some of the arguments "
                    "'num_return_vals', 'num_cpus', or 'num_gpus', like "
                    "'@ray.remote(num_return_vals=2)'.")
    assert len(args) == 0 and ("num_return_vals" in kwargs or
                               "num_cpus" in kwargs or
                               "num_gpus" in kwargs), error_string
    assert "function_id" not in kwargs
    return make_remote_decorator(num_return_vals, num_cpus, num_gpus)