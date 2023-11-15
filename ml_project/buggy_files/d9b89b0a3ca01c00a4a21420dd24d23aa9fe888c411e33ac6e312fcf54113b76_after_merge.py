def remote(*args, **kwargs):
    """This decorator is used to define remote functions and to define actors.

    Args:
        num_return_vals (int): The number of object IDs that a call to this
            function should return.
        num_cpus (int): The number of CPUs needed to execute this function.
        num_gpus (int): The number of GPUs needed to execute this function.
        resources: A dictionary mapping resource name to the required quantity
            of that resource.
        max_calls (int): The maximum number of tasks of this kind that can be
            run on a worker before the worker needs to be restarted.
        checkpoint_interval (int): The number of tasks to run between
            checkpoints of the actor state.
    """
    worker = global_worker

    def make_remote_decorator(num_return_vals, num_cpus, num_gpus, resources,
                              max_calls, checkpoint_interval, func_id=None):
        def remote_decorator(func_or_class):
            if inspect.isfunction(func_or_class) or is_cython(func_or_class):
                # Set the remote function default resources.
                resources["CPU"] = (DEFAULT_REMOTE_FUNCTION_CPUS
                                    if num_cpus is None else num_cpus)
                resources["GPU"] = (DEFAULT_REMOTE_FUNCTION_GPUS
                                    if num_gpus is None else num_gpus)

                function_properties = FunctionProperties(
                    num_return_vals=num_return_vals,
                    resources=resources,
                    max_calls=max_calls)
                return remote_function_decorator(func_or_class,
                                                 function_properties)
            if inspect.isclass(func_or_class):
                # Set the actor default resources.
                if num_cpus is None and num_gpus is None and resources == {}:
                    # In the default case, actors acquire no resources for
                    # their lifetime, and actor methods will require 1 CPU.
                    resources["CPU"] = DEFAULT_ACTOR_CREATION_CPUS_SIMPLE_CASE
                    actor_method_cpus = DEFAULT_ACTOR_METHOD_CPUS_SIMPLE_CASE
                else:
                    # If any resources are specified, then all resources are
                    # acquired for the actor's lifetime and no resources are
                    # associated with methods.
                    resources["CPU"] = (
                        DEFAULT_ACTOR_CREATION_CPUS_SPECIFIED_CASE
                        if num_cpus is None else num_cpus)
                    resources["GPU"] = (
                        DEFAULT_ACTOR_CREATION_GPUS_SPECIFIED_CASE
                        if num_gpus is None else num_gpus)
                    actor_method_cpus = (
                        DEFAULT_ACTOR_METHOD_CPUS_SPECIFIED_CASE)

                return worker.make_actor(func_or_class, resources,
                                         checkpoint_interval,
                                         actor_method_cpus)
            raise Exception("The @ray.remote decorator must be applied to "
                            "either a function or to a class.")

        def remote_function_decorator(func, function_properties):
            func_name = "{}.{}".format(func.__module__, func.__name__)
            if func_id is None:
                function_id = compute_function_id(func_name, func)
            else:
                function_id = func_id

            def func_call(*args, **kwargs):
                """This runs immediately when a remote function is called."""
                check_connected()
                check_main_thread()
                args = signature.extend_args(function_signature, args, kwargs)

                if _mode() == PYTHON_MODE:
                    # In PYTHON_MODE, remote calls simply execute the function.
                    # We copy the arguments to prevent the function call from
                    # mutating them and to match the usual behavior of
                    # immutable remote objects.
                    result = func(*copy.deepcopy(args))
                    return result
                objectids = _submit_task(function_id, args)
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
                raise Exception("Remote functions cannot be called directly. "
                                "Instead of running '{}()', try '{}.remote()'."
                                .format(func_name, func_name))
            func_invoker.remote = func_call
            func_invoker.executor = func_executor
            func_invoker.is_remote = True
            func_name = "{}.{}".format(func.__module__, func.__name__)
            func_invoker.func_name = func_name
            if sys.version_info >= (3, 0) or is_cython(func):
                func_invoker.__doc__ = func.__doc__
            else:
                func_invoker.func_doc = func.func_doc

            signature.check_signature_supported(func)
            function_signature = signature.extract_signature(func)

            # Everything ready - export the function
            if worker.mode in [SCRIPT_MODE, SILENT_MODE]:
                export_remote_function(function_id, func_name, func,
                                       func_invoker, function_properties)
            elif worker.mode is None:
                worker.cached_remote_functions_and_actors.append(
                    ("remote_function", (function_id, func_name, func,
                                         func_invoker, function_properties)))
            return func_invoker

        return remote_decorator

    # Handle resource arguments
    num_cpus = kwargs["num_cpus"] if "num_cpus" in kwargs else None
    num_gpus = kwargs["num_gpus"] if "num_gpus" in kwargs else None
    resources = kwargs.get("resources", {})
    if not isinstance(resources, dict):
        raise Exception("The 'resources' keyword argument must be a "
                        "dictionary, but received type {}."
                        .format(type(resources)))
    assert "CPU" not in resources, "Use the 'num_cpus' argument."
    assert "GPU" not in resources, "Use the 'num_gpus' argument."
    # Handle other arguments.
    num_return_vals = (kwargs["num_return_vals"] if "num_return_vals"
                       in kwargs else 1)
    max_calls = kwargs["max_calls"] if "max_calls" in kwargs else 0
    checkpoint_interval = (kwargs["checkpoint_interval"]
                           if "checkpoint_interval" in kwargs else -1)

    if _mode() == WORKER_MODE:
        if "function_id" in kwargs:
            function_id = kwargs["function_id"]
            return make_remote_decorator(num_return_vals, num_cpus, num_gpus,
                                         resources, max_calls,
                                         checkpoint_interval, function_id)

    if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
        # This is the case where the decorator is just @ray.remote.
        return make_remote_decorator(
            num_return_vals, num_cpus, num_gpus, resources,
            max_calls, checkpoint_interval)(args[0])
    else:
        # This is the case where the decorator is something like
        # @ray.remote(num_return_vals=2).
        error_string = ("The @ray.remote decorator must be applied either "
                        "with no arguments and no parentheses, for example "
                        "'@ray.remote', or it must be applied using some of "
                        "the arguments 'num_return_vals', 'resources', "
                        "or 'max_calls', like "
                        "'@ray.remote(num_return_vals=2, "
                        "resources={\"GPU\": 1})'.")
        assert len(args) == 0 and len(kwargs) > 0, error_string
        for key in kwargs:
            assert key in ["num_return_vals", "num_cpus", "num_gpus",
                           "resources", "max_calls",
                           "checkpoint_interval"], error_string
        assert "function_id" not in kwargs
        return make_remote_decorator(num_return_vals, num_cpus, num_gpus,
                                     resources, max_calls, checkpoint_interval)