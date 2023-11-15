    def execute_async(
        self,
        key: TaskInstanceKey,
        command: CommandType,
        queue: Optional[str] = None,
        executor_config: Optional[Any] = None,
    ) -> None:
        """Executes task asynchronously"""
        self.log.info('Add task %s with command %s with executor_config %s', key, command, executor_config)
        kube_executor_config = PodGenerator.from_obj(executor_config)
        if executor_config:
            pod_template_file = executor_config.get("pod_template_override", None)
        else:
            pod_template_file = None
        if not self.task_queue:
            raise AirflowException(NOT_STARTED_MESSAGE)
        self.event_buffer[key] = (State.QUEUED, self.scheduler_job_id)
        self.task_queue.put((key, command, kube_executor_config, pod_template_file))