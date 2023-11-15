    def _task_table(self, task_id):
        """Fetch and parse the task table information for a single task ID.

        Args:
            task_id_binary: A string of bytes with the task ID to get
                information about.

        Returns:
            A dictionary with information about the task ID in question.
                TASK_STATUS_MAPPING should be used to parse the "State" field
                into a human-readable string.
        """
        task_table_response = self._execute_command(task_id,
                                                    "RAY.TASK_TABLE_GET",
                                                    task_id.id())
        if task_table_response is None:
            raise Exception("There is no entry for task ID {} in the task "
                            "table.".format(binary_to_hex(task_id.id())))
        task_table_message = TaskReply.GetRootAsTaskReply(task_table_response,
                                                          0)
        task_spec = task_table_message.TaskSpec()
        task_spec = ray.local_scheduler.task_from_string(task_spec)

        task_spec_info = {
            "DriverID": binary_to_hex(task_spec.driver_id().id()),
            "TaskID": binary_to_hex(task_spec.task_id().id()),
            "ParentTaskID": binary_to_hex(task_spec.parent_task_id().id()),
            "ParentCounter": task_spec.parent_counter(),
            "ActorID": binary_to_hex(task_spec.actor_id().id()),
            "ActorCreationID":
                binary_to_hex(task_spec.actor_creation_id().id()),
            "ActorCreationDummyObjectID":
                binary_to_hex(task_spec.actor_creation_dummy_object_id().id()),
            "ActorCounter": task_spec.actor_counter(),
            "FunctionID": binary_to_hex(task_spec.function_id().id()),
            "Args": task_spec.arguments(),
            "ReturnObjectIDs": task_spec.returns(),
            "RequiredResources": task_spec.required_resources()}

        execution_dependencies_message = (
            TaskExecutionDependencies.GetRootAsTaskExecutionDependencies(
                task_table_message.ExecutionDependencies(), 0))
        execution_dependencies = [
            ray.local_scheduler.ObjectID(
                execution_dependencies_message.ExecutionDependencies(i))
            for i in range(
                execution_dependencies_message.ExecutionDependenciesLength())]

        # TODO(rkn): The return fields ExecutionDependenciesString and
        # ExecutionDependencies are redundant, so we should remove
        # ExecutionDependencies. However, it is currently used in monitor.py.

        return {"State": task_table_message.State(),
                "LocalSchedulerID": binary_to_hex(
                    task_table_message.LocalSchedulerId()),
                "ExecutionDependenciesString":
                    task_table_message.ExecutionDependencies(),
                "ExecutionDependencies": execution_dependencies,
                "SpillbackCount":
                    task_table_message.SpillbackCount(),
                "TaskSpec": task_spec_info}