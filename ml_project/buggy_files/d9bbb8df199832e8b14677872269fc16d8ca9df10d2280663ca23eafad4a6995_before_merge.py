def register_actor_signatures(worker, driver_id, class_name,
                              actor_method_names,
                              actor_method_num_return_vals):
    """Register an actor's method signatures in the worker.

    Args:
        worker: The worker to register the signatures on.
        driver_id: The ID of the driver that this actor is associated with.
        actor_id: The ID of the actor.
        actor_method_names: The names of the methods to register.
        actor_method_num_return_vals: A list of the number of return values for
            each of the actor's methods.
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
            FunctionProperties(num_return_vals=num_return_vals + 1,
                               resources={"CPU": 1},
                               max_calls=0))