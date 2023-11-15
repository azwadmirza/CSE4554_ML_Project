        def __del__(self):
            """Kill the worker that is running this actor."""
            # TODO(swang): Also clean up forked actor handles.
            # Kill the worker if this is the original actor handle, created
            # with Class.remote().
            if (ray.worker.global_worker.connected and
                    self._ray_actor_handle_id.id() == ray.worker.NIL_ACTOR_ID):
                # TODO(rkn): Should we be passing in the actor cursor as a
                # dependency here?
                self._actor_method_call("__ray_terminate__",
                                        args=[self._ray_actor_id.id()])