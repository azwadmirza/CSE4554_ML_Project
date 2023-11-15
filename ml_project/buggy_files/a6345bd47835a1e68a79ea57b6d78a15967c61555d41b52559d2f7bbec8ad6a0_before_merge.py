    def get(self):
        """Get a dictionary of the current_context.

        For fields that are not available (for example actor id inside a task)
        won't be included in the field.

        Returns:
            dict: Dictionary of the current context.
        """
        context = {
            "job_id": self.job_id,
            "node_id": self.node_id,
            "task_id": self.task_id,
            "actor_id": self.actor_id
        }
        # Remove fields that are None.
        return {
            key: value
            for key, value in context.items() if value is not None
        }