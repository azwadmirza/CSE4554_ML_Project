    def _serialization_helper(self, ray_forking):
        """This is defined in order to make pickling work.

        Args:
            ray_forking: True if this is being called because Ray is forking
                the actor handle and false if it is being called by pickling.

        Returns:
            A dictionary of the information needed to reconstruct the object.
        """
        state = {
            "actor_id": self._ray_actor_id.id(),
            "class_name": self._ray_class_name,
            "actor_forks": self._ray_actor_forks,
            "actor_cursor": self._ray_actor_cursor.id(),
            "actor_counter": 0,  # Reset the actor counter.
            "actor_method_names": self._ray_actor_method_names,
            "method_signatures": self._ray_method_signatures,
            "method_num_return_vals": self._ray_method_num_return_vals,
            "actor_creation_dummy_object_id": self.
            _ray_actor_creation_dummy_object_id.id(),
            "actor_method_cpus": self._ray_actor_method_cpus,
            "actor_driver_id": self._ray_actor_driver_id.id(),
            "previous_actor_handle_id": self._ray_actor_handle_id.id()
            if self._ray_actor_handle_id else None,
            "ray_forking": ray_forking
        }

        if ray_forking:
            self._ray_actor_forks += 1

        return state