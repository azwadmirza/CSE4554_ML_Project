def fetch_and_register_actor(actor_class_key, worker):
    """Import an actor.

    This will be called by the worker's import thread when the worker receives
    the actor_class export, assuming that the worker is an actor for that
    class.
    """
    actor_id_str = worker.actor_id
    (driver_id, class_id, class_name,
     module, pickled_class, checkpoint_interval,
     actor_method_names,
     actor_method_num_return_vals) = worker.redis_client.hmget(
         actor_class_key, ["driver_id", "class_id", "class_name", "module",
                           "class", "checkpoint_interval",
                           "actor_method_names",
                           "actor_method_num_return_vals"])

    actor_name = class_name.decode("ascii")
    module = module.decode("ascii")
    checkpoint_interval = int(checkpoint_interval)
    actor_method_names = json.loads(actor_method_names.decode("ascii"))
    actor_method_num_return_vals = json.loads(
        actor_method_num_return_vals.decode("ascii"))

    # Create a temporary actor with some temporary methods so that if the actor
    # fails to be unpickled, the temporary actor can be used (just to produce
    # error messages and to prevent the driver from hanging).
    class TemporaryActor(object):
        pass
    worker.actors[actor_id_str] = TemporaryActor()
    worker.actor_checkpoint_interval = checkpoint_interval

    def temporary_actor_method(*xs):
        raise Exception("The actor with name {} failed to be imported, and so "
                        "cannot execute this method".format(actor_name))
    # Register the actor method signatures.
    register_actor_signatures(worker, driver_id, class_name,
                              actor_method_names, actor_method_num_return_vals)
    # Register the actor method executors.
    for actor_method_name in actor_method_names:
        function_id = compute_actor_method_function_id(class_name,
                                                       actor_method_name).id()
        temporary_executor = make_actor_method_executor(worker,
                                                        actor_method_name,
                                                        temporary_actor_method,
                                                        actor_imported=False)
        worker.functions[driver_id][function_id] = (actor_method_name,
                                                    temporary_executor)
        worker.num_task_executions[driver_id][function_id] = 0

    try:
        unpickled_class = pickle.loads(pickled_class)
        worker.actor_class = unpickled_class
    except Exception:
        # If an exception was thrown when the actor was imported, we record the
        # traceback and notify the scheduler of the failure.
        traceback_str = ray.utils.format_error_message(traceback.format_exc())
        # Log the error message.
        push_error_to_driver(worker.redis_client, "register_actor_signatures",
                             traceback_str, driver_id,
                             data={"actor_id": actor_id_str})
        # TODO(rkn): In the future, it might make sense to have the worker exit
        # here. However, currently that would lead to hanging if someone calls
        # ray.get on a method invoked on the actor.
    else:
        # TODO(pcm): Why is the below line necessary?
        unpickled_class.__module__ = module
        worker.actors[actor_id_str] = unpickled_class.__new__(unpickled_class)
        actor_methods = inspect.getmembers(
            unpickled_class, predicate=(lambda x: (inspect.isfunction(x) or
                                                   inspect.ismethod(x) or
                                                   is_cython(x))))
        for actor_method_name, actor_method in actor_methods:
            function_id = compute_actor_method_function_id(
                class_name, actor_method_name).id()
            executor = make_actor_method_executor(worker, actor_method_name,
                                                  actor_method,
                                                  actor_imported=True)
            worker.functions[driver_id][function_id] = (actor_method_name,
                                                        executor)
            # We do not set worker.function_properties[driver_id][function_id]
            # because we currently do need the actor worker to submit new tasks
            # for the actor.

        # Store some extra information that will be used when the actor exits
        # to release GPU resources.
        worker.driver_id = binary_to_hex(driver_id)
        local_scheduler_id = worker.redis_client.hget(
            b"Actor:" + actor_id_str, "local_scheduler_id")
        worker.local_scheduler_id = binary_to_hex(local_scheduler_id)