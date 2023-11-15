    def submit_task(self, function_id, args, actor_id=None,
                    actor_handle_id=None, actor_counter=0,
                    is_actor_checkpoint_method=False,
                    execution_dependencies=None):
        """Submit a remote task to the scheduler.

        Tell the scheduler to schedule the execution of the function with ID
        function_id with arguments args. Retrieve object IDs for the outputs of
        the function from the scheduler and immediately return them.

        Args:
            function_id: The ID of the function to execute.
            args: The arguments to pass into the function. Arguments can be
                object IDs or they can be values. If they are values, they must
                be serializable objecs.
            actor_id: The ID of the actor that this task is for.
            actor_counter: The counter of the actor task.
            is_actor_checkpoint_method: True if this is an actor checkpoint
                task and false otherwise.
        """
        with log_span("ray:submit_task", worker=self):
            check_main_thread()
            if actor_id is None:
                assert actor_handle_id is None
                actor_id = ray.local_scheduler.ObjectID(NIL_ACTOR_ID)
                actor_handle_id = ray.local_scheduler.ObjectID(NIL_ACTOR_ID)
            else:
                assert actor_handle_id is not None
            # Put large or complex arguments that are passed by value in the
            # object store first.
            args_for_local_scheduler = []
            for arg in args:
                if isinstance(arg, ray.local_scheduler.ObjectID):
                    args_for_local_scheduler.append(arg)
                elif isinstance(arg, ray.actor.ActorHandleParent):
                    args_for_local_scheduler.append(put(
                        ray.actor.wrap_actor_handle(arg)))
                elif ray.local_scheduler.check_simple_value(arg):
                    args_for_local_scheduler.append(arg)
                else:
                    args_for_local_scheduler.append(put(arg))

            # By default, there are no execution dependencies.
            if execution_dependencies is None:
                execution_dependencies = []

            # Look up the various function properties.
            function_properties = self.function_properties[
                self.task_driver_id.id()][function_id.id()]

            # Submit the task to local scheduler.
            task = ray.local_scheduler.Task(
                self.task_driver_id,
                ray.local_scheduler.ObjectID(function_id.id()),
                args_for_local_scheduler,
                function_properties.num_return_vals,
                self.current_task_id,
                self.task_index,
                actor_id,
                actor_handle_id,
                actor_counter,
                is_actor_checkpoint_method,
                execution_dependencies,
                function_properties.resources)
            # Increment the worker's task index to track how many tasks have
            # been submitted by the current task so far.
            self.task_index += 1
            self.local_scheduler_client.submit(task)

            return task.returns()