    def _become_actor(self, task):
        """Turn this worker into an actor.

        Args:
            task: The actor creation task.
        """
        assert self.actor_id == NIL_ACTOR_ID
        arguments = task.arguments()
        assert len(arguments) == 1
        self.actor_id = task.actor_creation_id().id()
        class_id = arguments[0]

        key = b"ActorClass:" + class_id

        # Wait for the actor class key to have been imported by the import
        # thread. TODO(rkn): It shouldn't be possible to end up in an infinite
        # loop here, but we should push an error to the driver if too much time
        # is spent here.
        while key not in self.imported_actor_classes:
            time.sleep(0.001)

        with self.lock:
            self.fetch_and_register_actor(key, task.required_resources(), self)