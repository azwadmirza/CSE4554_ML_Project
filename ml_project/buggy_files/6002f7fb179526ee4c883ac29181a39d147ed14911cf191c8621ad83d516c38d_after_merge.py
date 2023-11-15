    def _deserialization_helper(self, state, ray_forking):
        """This is defined in order to make pickling work.

        Args:
            state: The serialized state of the actor handle.
            ray_forking: True if this is being called because Ray is forking
                the actor handle and false if it is being called by pickling.
        """
        worker = ray.worker.get_global_worker()
        worker.check_connected()
        ray.worker.check_main_thread()

        if state["ray_forking"]:
            actor_handle_id = compute_actor_handle_id(
                ray.ObjectID(state["previous_actor_handle_id"]),
                state["actor_forks"])
        else:
            actor_handle_id = None

        # This is the driver ID of the driver that owns the actor, not
        # necessarily the driver that owns this actor handle.
        actor_driver_id = ray.ObjectID(state["actor_driver_id"])

        self.__init__(
            ray.ObjectID(state["actor_id"]),
            state["class_name"],
            ray.ObjectID(state["actor_cursor"])
            if state["actor_cursor"] is not None else None,
            state["actor_counter"],
            state["actor_method_names"],
            state["method_signatures"],
            state["method_num_return_vals"],
            ray.ObjectID(state["actor_creation_dummy_object_id"])
            if state["actor_creation_dummy_object_id"] is not None else None,
            state["actor_method_cpus"],
            actor_driver_id,
            actor_handle_id=actor_handle_id,
            previous_actor_handle_id=ray.ObjectID(
                state["previous_actor_handle_id"]))