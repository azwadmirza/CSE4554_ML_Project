    def get(self):
        """Get a dictionary of the current context.

        Fields that are not available (e.g., actor ID inside a task) won't be
        included in the field.

        Returns:
            dict: Dictionary of the current context.
        """
        context = {
            "job_id": self.job_id,
            "node_id": self.node_id,
        }
        if self.worker.mode == ray.worker.WORKER_MODE:
            if self.task_id is not None:
                context["task_id"] = self.task_id
            if self.actor_id is not None:
                context["actor_id"] = self.actor_id

        return context