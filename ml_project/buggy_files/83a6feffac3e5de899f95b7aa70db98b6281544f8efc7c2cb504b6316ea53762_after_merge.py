        def _actor_method_call(self, method_name, args=None, kwargs=None,
                               dependency=None):
            """Method execution stub for an actor handle.

            This is the function that executes when
            `actor.method_name.remote(*args, **kwargs)` is called. Instead of
            executing locally, the method is packaged as a task and scheduled
            to the remote actor instance.

            Args:
                self: The local actor handle.
                method_name: The name of the actor method to execute.
                args: A list of arguments for the actor method.
                kwargs: A dictionary of keyword arguments for the actor method.
                dependency: The object ID that this method is dependent on.
                    Defaults to None, for no dependencies. Most tasks should
                    pass in the dummy object returned by the preceding task.
                    Some tasks, such as checkpoint and terminate methods, have
                    no dependencies.

            Returns:
                object_ids: A list of object IDs returned by the remote actor
                    method.
            """
            ray.worker.check_connected()
            ray.worker.check_main_thread()
            function_signature = self._ray_method_signatures[method_name]
            if args is None:
                args = []
            if kwargs is None:
                kwargs = {}
            args = signature.extend_args(function_signature, args, kwargs)

            # Execute functions locally if Ray is run in PYTHON_MODE
            # Copy args to prevent the function from mutating them.
            if ray.worker.global_worker.mode == ray.PYTHON_MODE:
                return getattr(
                    ray.worker.global_worker.actors[self._ray_actor_id],
                    method_name)(*copy.deepcopy(args))

            # Add the execution dependency.
            if dependency is None:
                execution_dependencies = []
            else:
                execution_dependencies = [dependency]

            is_actor_checkpoint_method = (method_name == "__ray_checkpoint__")

            function_id = compute_actor_method_function_id(
                self._ray_class_name, method_name)
            object_ids = ray.worker.global_worker.submit_task(
                function_id, args, actor_id=self._ray_actor_id,
                actor_handle_id=self._ray_actor_handle_id,
                actor_counter=self._ray_actor_counter,
                is_actor_checkpoint_method=is_actor_checkpoint_method,
                actor_creation_dummy_object_id=(
                    self._ray_actor_creation_dummy_object_id),
                execution_dependencies=execution_dependencies)
            # Update the actor counter and cursor to reflect the most recent
            # invocation.
            self._ray_actor_counter += 1
            self._ray_actor_cursor = object_ids.pop()

            # The last object returned is the dummy object that should be
            # passed in to the next actor method. Do not return it to the user.
            if len(object_ids) == 1:
                return object_ids[0]
            elif len(object_ids) > 1:
                return object_ids