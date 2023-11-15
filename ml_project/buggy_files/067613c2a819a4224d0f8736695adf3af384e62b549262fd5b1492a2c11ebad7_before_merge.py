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