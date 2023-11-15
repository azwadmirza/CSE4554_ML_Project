def register_actor_signatures(worker, driver_id, class_id, class_name,
                              actor_method_names,
                              actor_method_num_return_vals,
                              actor_creation_resources=None,
                              actor_method_cpus=None):
    """Register an actor's method signatures in the worker.

    Args:
        worker: The worker to register the signatures on.
        driver_id: The ID of the driver that this actor is associated with.
        class_id: The ID of the actor class.
        class_name: The name of the actor class.
        actor_method_names: The names of the methods to register.
        actor_method_num_return_vals: A list of the number of return values for
            each of the actor's methods.
        actor_creation_resources: The resources required by the actor creation
            task.
        actor_method_cpus: The number of CPUs required by each actor method.
    """
    assert len(actor_method_names) == len(actor_method_num_return_vals)
    for actor_method_name, num_return_vals in zip(
            actor_method_names, actor_method_num_return_vals):
        # TODO(rkn): When we create a second actor, we are probably overwriting
        # the values from the first actor here. This may or may not be a
        # problem.
        function_id = compute_actor_method_function_id(class_name,
                                                       actor_method_name).id()
        worker.function_properties[driver_id][function_id] = (
            # The extra return value is an actor dummy object.
            # In the cases where actor_method_cpus is None, that value should
            # never be used.
            FunctionProperties(num_return_vals=num_return_vals + 1,
                               resources={"CPU": actor_method_cpus},
                               max_calls=0))

    if actor_creation_resources is not None:
        # Also register the actor creation task.
        function_id = compute_actor_creation_function_id(class_id)
        worker.function_properties[driver_id][function_id.id()] = (
            # The extra return value is an actor dummy object.
            FunctionProperties(num_return_vals=0 + 1,
                               resources=actor_creation_resources,
                               max_calls=0))