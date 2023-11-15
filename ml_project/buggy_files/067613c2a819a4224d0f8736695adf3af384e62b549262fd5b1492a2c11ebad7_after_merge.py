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