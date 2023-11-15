def export_actor(actor_id, class_id, class_name, actor_method_names,
                 actor_method_num_return_vals, resources, worker):
    """Export an actor to redis.

    Args:
        actor_id (common.ObjectID): The ID of the actor.
        class_id (str): A random ID for the actor class.
        class_name (str): The actor class name.
        actor_method_names (list): A list of the names of this actor's methods.
        actor_method_num_return_vals: A list of the number of return values for
            each of the actor's methods.
        resources: A dictionary mapping resource name to the quantity of that
            resource required by the actor.
    """
    ray.worker.check_main_thread()
    if worker.mode is None:
        raise Exception("Actors cannot be created before Ray has been "
                        "started. You can start Ray with 'ray.init()'.")

    driver_id = worker.task_driver_id.id()
    register_actor_signatures(worker, driver_id, class_name,
                              actor_method_names, actor_method_num_return_vals)

    # Select a local scheduler for the actor.
    key = b"Actor:" + actor_id.id()
    local_scheduler_id = select_local_scheduler(
        worker.task_driver_id.id(), ray.global_state.local_schedulers(),
        resources.get("GPU", 0), worker.redis_client)
    assert local_scheduler_id is not None

    # We must put the actor information in Redis before publishing the actor
    # notification so that when the newly created actor attempts to fetch the
    # information from Redis, it is already there.
    driver_id = worker.task_driver_id.id()
    worker.redis_client.hmset(key, {"class_id": class_id,
                                    "driver_id": driver_id,
                                    "local_scheduler_id": local_scheduler_id,
                                    "num_gpus": resources.get("GPU", 0),
                                    "removed": False})

    # TODO(rkn): There is actually no guarantee that the local scheduler that
    # we are publishing to has already subscribed to the actor_notifications
    # channel. Therefore, this message may be missed and the workload will
    # hang. This is a bug.
    ray.utils.publish_actor_creation(actor_id.id(), driver_id,
                                     local_scheduler_id, False,
                                     worker.redis_client)