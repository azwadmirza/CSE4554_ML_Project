def export_actor(actor_id, class_id, class_name, actor_method_names,
                 actor_method_num_return_vals, actor_creation_resources,
                 actor_method_cpus, worker):
    """Export an actor to redis.

    Args:
        actor_id (common.ObjectID): The ID of the actor.
        class_id (str): A random ID for the actor class.
        class_name (str): The actor class name.
        actor_method_names (list): A list of the names of this actor's methods.
        actor_method_num_return_vals: A list of the number of return values for
            each of the actor's methods.
        actor_creation_resources: A dictionary mapping resource name to the
            quantity of that resource required by the actor.
        actor_method_cpus: The number of CPUs required by actor methods.
    """
    ray.worker.check_main_thread()
    if worker.mode is None:
        raise Exception("Actors cannot be created before Ray has been "
                        "started. You can start Ray with 'ray.init()'.")

    driver_id = worker.task_driver_id.id()
    register_actor_signatures(
        worker, driver_id, class_id, class_name, actor_method_names,
        actor_method_num_return_vals,
        actor_creation_resources=actor_creation_resources,
        actor_method_cpus=actor_method_cpus)

    args = [class_id]
    function_id = compute_actor_creation_function_id(class_id)
    return worker.submit_task(function_id, args, actor_creation_id=actor_id)[0]