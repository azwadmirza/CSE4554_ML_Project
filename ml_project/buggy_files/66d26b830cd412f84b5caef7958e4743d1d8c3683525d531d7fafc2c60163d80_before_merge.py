    def __init__(self, actor_id, actor_handle_id, actor_cursor, actor_counter,
                 actor_method_names, actor_method_num_return_vals,
                 method_signatures, checkpoint_interval, class_name):
        self.actor_id = actor_id
        self.actor_handle_id = actor_handle_id
        self.actor_cursor = actor_cursor
        self.actor_counter = actor_counter
        self.actor_method_names = actor_method_names
        self.actor_method_num_return_vals = actor_method_num_return_vals
        # TODO(swang): Fetch this information from Redis so that we don't have
        # to fall back to pickle.
        self.method_signatures = method_signatures
        self.checkpoint_interval = checkpoint_interval
        self.class_name = class_name