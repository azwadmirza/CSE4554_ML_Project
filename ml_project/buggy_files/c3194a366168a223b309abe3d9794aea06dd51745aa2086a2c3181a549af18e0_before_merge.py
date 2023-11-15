def unwrap_actor_handle(worker, wrapper):
    """Make an ActorHandle from the stored fields.

    Args:
        worker: The worker that is unwrapping the actor handle.
        wrapper: An ActorHandleWrapper instance to unwrap.

    Returns:
        The unwrapped ActorHandle instance.
    """
    driver_id = worker.task_driver_id.id()
    register_actor_signatures(worker, driver_id, wrapper.class_name,
                              wrapper.actor_method_names,
                              wrapper.actor_method_num_return_vals)

    actor_handle_class = make_actor_handle_class(wrapper.class_name)
    actor_object = actor_handle_class.__new__(actor_handle_class)
    actor_object._manual_init(
        wrapper.actor_id,
        wrapper.actor_handle_id,
        wrapper.actor_cursor,
        wrapper.actor_counter,
        wrapper.actor_method_names,
        wrapper.actor_method_num_return_vals,
        wrapper.method_signatures,
        wrapper.checkpoint_interval)
    return actor_object