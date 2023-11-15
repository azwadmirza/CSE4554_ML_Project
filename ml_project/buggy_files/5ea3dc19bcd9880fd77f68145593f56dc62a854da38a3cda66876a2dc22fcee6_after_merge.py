def wrap_actor_handle(actor_handle):
    """Wrap the ActorHandle to store the fields.

    Args:
        actor_handle: The ActorHandle instance to wrap.

    Returns:
        An ActorHandleWrapper instance that stores the ActorHandle's fields.
    """
    wrapper = ActorHandleWrapper(
        actor_handle._ray_actor_id,
        actor_handle._ray_class_id,
        compute_actor_handle_id(actor_handle._ray_actor_handle_id,
                                actor_handle._ray_actor_forks),
        actor_handle._ray_actor_cursor,
        0,  # Reset the actor counter.
        actor_handle._ray_actor_method_names,
        actor_handle._ray_actor_method_num_return_vals,
        actor_handle._ray_method_signatures,
        actor_handle._ray_checkpoint_interval,
        actor_handle._ray_class_name,
        actor_handle._ray_actor_creation_dummy_object_id,
        actor_handle._ray_actor_creation_resources,
        actor_handle._ray_actor_method_cpus)
    actor_handle._ray_actor_forks += 1
    return wrapper