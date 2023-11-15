        def _manual_init(self, actor_id, actor_handle_id, actor_cursor,
                         actor_counter, actor_method_names,
                         actor_method_num_return_vals, method_signatures,
                         checkpoint_interval):
            self._ray_actor_id = actor_id
            self._ray_actor_handle_id = actor_handle_id
            self._ray_actor_cursor = actor_cursor
            self._ray_actor_counter = actor_counter
            self._ray_actor_method_names = actor_method_names
            self._ray_actor_method_num_return_vals = (
                actor_method_num_return_vals)
            self._ray_method_signatures = method_signatures
            self._ray_checkpoint_interval = checkpoint_interval
            self._ray_class_name = class_name
            self._ray_actor_forks = 0