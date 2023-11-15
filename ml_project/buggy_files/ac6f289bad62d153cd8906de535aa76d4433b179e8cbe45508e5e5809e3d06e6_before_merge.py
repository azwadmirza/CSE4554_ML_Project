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
            "ActorCounter": task_spec.actor_counter(),
            "FunctionID": binary_to_hex(task_spec.function_id().id()),
            "Args": task_spec.arguments(),
            "ReturnObjectIDs": task_spec.returns(),
            "RequiredResources": task_spec.required_resources()}

        return {"State": task_table_message.State(),
                "LocalSchedulerID": binary_to_hex(
                    task_table_message.LocalSchedulerId()),
                "ExecutionDependenciesString":
                    task_table_message.ExecutionDependencies(),
                "SpillbackCount":
                    task_table_message.SpillbackCount(),
                "TaskSpec": task_spec_info}