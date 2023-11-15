    def __init__(self, actor_id, class_id, actor_handle_id, actor_cursor,
                 actor_counter, actor_method_names,
                 actor_method_num_return_vals, method_signatures,
                 checkpoint_interval, class_name,
                 actor_creation_dummy_object_id,
                 actor_creation_resources, actor_method_cpus):
        # TODO(rkn): Some of these fields are probably not necessary. We should
        # strip out the unnecessary fields to keep actor handles lightweight.
        self.actor_id = actor_id
        self.class_id = class_id
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
        self.actor_creation_dummy_object_id = actor_creation_dummy_object_id
        self.actor_creation_resources = actor_creation_resources
        self.actor_method_cpus = actor_method_cpus