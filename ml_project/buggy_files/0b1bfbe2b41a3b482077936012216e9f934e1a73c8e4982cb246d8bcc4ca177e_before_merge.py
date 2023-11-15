    def make_remote_decorator(num_return_vals, resources, max_calls,
                              checkpoint_interval, func_id=None):
        def remote_decorator(func_or_class):
            if inspect.isfunction(func_or_class) or is_cython(func_or_class):
                function_properties = FunctionProperties(
                    num_return_vals=num_return_vals,
                    resources=resources,
                    max_calls=max_calls)
                return remote_function_decorator(func_or_class,
                                                 function_properties)
            if inspect.isclass(func_or_class):
                return worker.make_actor(func_or_class, resources,
                                         checkpoint_interval)
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